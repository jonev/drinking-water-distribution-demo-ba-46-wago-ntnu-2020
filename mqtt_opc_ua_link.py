from opcua import Client, ua
import paho.mqtt.client as mqtt
from threading import Thread, Lock
import time
import json
import hashlib

# Global variables
variables = {}
hashs = {}  # Storing a hash of the object to be able to compare two objects fast
hashsLock = Lock()  # hashs are used in multiple threads
sampleTime = 30  # For testing
## Opc UA
opcUaServer = "172.17.0.1"  # Host of docker
opcUaServerUsername = "admin"
opcUaServerPassword = "wago"
opcUaNs = 4  # Address
opcUaIdPrefix = "|var|WAGO 750-8214 PFC200 G2 2ETH RS CAN.PFCx00_SmartCoupler.HMI"
## MQTT
mqttBroker = "broker.hivemq.com"
mqttPort = 1883
mqttTopicPublishData = "ba/wago/opcua/test/plcpub"
mqttTopicSubscribeData = "ba/wago/opcua/test/plcsub"
mqttPublishSuffix = "Pv"  # Published every sample, other tags are pulished on data change


def on_connect(client, userdata, flags, rc):
    print("MQTT Connected with result code " + str(rc))
    client.subscribe(mqttTopicSubscribeData)


def on_message(client, userdata, msg):
    global hashsLock
    try:
        receivedObject = json.loads(str(msg.payload, encoding="utf-8"))
        # Generate new hash
        newValueHash = hashlib.md5(receivedObject.__str__().encode("utf-8")).hexdigest()
        # Store hash
        with hashsLock:  # Sending data only on change, therefor no need to check for change
            hashs[receivedObject["_id"]] = newValueHash
        # Write to opc ua by getting the children recursive
        topLevelObject = clientPlc.get_node(
            "ns=" + str(opcUaNs) + ";s=" + opcUaIdPrefix + "." + receivedObject["_id"]
        )
        setChildrenRecursive(receivedObject, topLevelObject.get_children())
    except Exception as e:
        print(e)


def setChildrenRecursive(pObject, OpcNodes):
    for node in OpcNodes:
        children = node.get_children()
        tagname = getTagname(node)
        if len(children) == 0:
            value = pObject[tagname]
            if type(value) is str:
                node.set_value(value)
            elif type(value) is bool:
                node.set_value(value)
            elif type(value) is float:
                node.set_value(value, varianttype=ua.VariantType.Float)
            else:
                raise Exception("Type not found")
        else:
            setChildrenRecursive(pObject[tagname], children)


# OPC UA
clientPlc = Client("opc.tcp://" + opcUaServer + ":4840")
clientPlc.set_user(opcUaServerUsername)
clientPlc.set_password(opcUaServerPassword)

# MQTT
mqttClient = mqtt.Client()
mqttClient.on_connect = on_connect
mqttClient.on_message = on_message


def getChildrenRecursive(pObject, OpcNodes):
    for node in OpcNodes:
        children = node.get_children()
        tagname = getTagname(node)
        if len(children) == 0:
            pObject[tagname] = node.get_value()
        else:
            pObject[tagname] = {}
            getChildrenRecursive(pObject[tagname], children)


def getTagname(node):
    path = node.nodeid.Identifier
    position = path.rfind(".")
    return path[position + 1 :]


try:
    # Init
    print("Connecting to Opc.")
    clientPlc.connect()
    if clientPlc is None:
        raise Exception("Opc connection failed")
    print("Connected")
    nodesUnderPrefix = clientPlc.get_node("ns=" + str(opcUaNs) + ";s=" + opcUaIdPrefix)

    print("Connecting to MQTT broker.")
    mqttClient.connect(mqttBroker, mqttPort, 60)
    mqttThread = Thread(target=mqttClient.loop_forever, args=())
    mqttThread.start()
    print("Waiting for MQTT to connect...")
    time.sleep(2)

    while True:  # Read data from OPC UA and Publish data to MQTT loop
        topLevelOpcNodes = (
            nodesUnderPrefix.get_children()
        )  # Nodes are initialized each loop -> no need for restart if there are new nodes
        if len(topLevelOpcNodes) == 0:
            raise Exception("No tags where found")
        for topLevelOpcNode in topLevelOpcNodes:
            tagname = getTagname(topLevelOpcNode)
            pObject = {}  # Building python object, then converting to json before sending
            getChildrenRecursive(pObject, topLevelOpcNode.get_children())
            # Publishing
            jsonStringOfObject = json.dumps(pObject)
            if mqttPublishSuffix in tagname:
                mqttClient.publish(mqttTopicPublishData, payload=jsonStringOfObject)
            else:
                # Hash
                newValueHash = hashlib.md5(pObject.__str__().encode("utf-8")).hexdigest()
                with hashsLock:
                    if tagname in hashs:
                        # Compare
                        if hashs[tagname] != newValueHash:
                            mqttClient.publish(mqttTopicPublishData, payload=jsonStringOfObject)
                            # Publish and save hash
                            hashs[tagname] = newValueHash
                        # Or nothing
                    else:
                        # Tagname does not exist in hashs
                        # Save hash
                        hashs[tagname] = newValueHash
                        # Publish
                        mqttClient.publish(mqttTopicPublishData, payload=jsonStringOfObject)
        time.sleep(sampleTime)

except Exception as e:
    print(e)
finally:
    if clientPlc is not None:
        clientPlc.disconnect()
    mqttClient.disconnect()
