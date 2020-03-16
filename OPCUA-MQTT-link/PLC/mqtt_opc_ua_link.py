from opcua import Client, ua, Node
import paho.mqtt.client as mqtt
from threading import Thread, Lock
from dotenv import load_dotenv
import time
import datetime
import json
import hashlib
import os
import logging
import copy

logging.basicConfig(level=logging.WARNING)
logging.info("Starting OPC-UA - MQTT link")
load_dotenv()
# Global variables
tags = {}
nodes = {}
hashs = {}  # Storing a hash of the object to be able to compare two objects fast
cmdPublishIntervall = 6
cmdPublishCounter = 0
hashsLock = Lock()  # hashs are used in multiple threads
publishLoopWaitTime = int(os.getenv("WAIT_TIME"))  # For testing
## Opc UA
opcUaServer = os.getenv("OPC_UA_SERVER")  # Host of docker "192.168.0.15"
opcUaServerUsername = os.getenv("OPC_UA_SERVER_USERNAME")
opcUaServerPassword = os.getenv("OPC_UA_SERVER_PASSWORD")
opcUaNs = int(os.getenv("OPC_UA_NS"))  # Address
opcUaIdPrefix = os.getenv("OPC_UA_ID_PREFIX")
## MQTT
mqttBroker = os.getenv("MQTT_BROKER")
mqttPort = int(os.getenv("MQTT_PORT"))
mqttTopicPublishData = os.getenv("MQTT_TOPIC_PUBLISHDATA")
mqttTopicSubscribeData = os.getenv("MQTT_TOPIC_SUBSCRIBEDATA")
mqttPublishPvSuffix = os.getenv(
    "MQTT_PUBLISH_PV_SUFFIX"
)  # Published every sample, other tags are pulished on data change
logging.info(
    "Evn: OpcUaServer: "
    + opcUaServer
    + ", OpcUaIdPrefix"
    + opcUaIdPrefix
    + ", MqttBroker: "
    + mqttBroker
)


def on_mqtt_connect(client, userdata, flags, rc):
    logging.info("MQTT Connected with result code " + str(rc))
    client.subscribe(mqttTopicSubscribeData)


def on_received_mqtt_message(client, userdata, msg):
    global hashsLock
    try:
        receivedObject = json.loads(str(msg.payload, encoding="utf-8"))
        # If plc receive empty objects, it send an object with values in return, immediately
        if receivedObject["_type"] == "":
            tagname = receivedObject["_tagId"]
            logging.warning("HMI is missing data and requesting: " + tagname)
            topLevelObject = clientPlc.get_node(
                "ns=" + str(opcUaNs) + ";s=" + opcUaIdPrefix + "." + tagname
            )
            pObject = tags[tagname]
            getValuesFromNodes(pObject, nodes[tagname])
            del pObject["_timestamp"]
            newHash = hashlib.md5(pObject.__str__().encode("utf-8")).hexdigest()
            pObject["_timestamp"] = str(datetime.datetime.now())
            # Publish and save hash
            mqttClient.publish(mqttTopicPublishData, payload=json.dumps(pObject))
            hashs[tagname] = newHash
            return

        # Generate new hash
        del receivedObject["_timestamp"]
        newHash = hashlib.md5(receivedObject.__str__().encode("utf-8")).hexdigest()
        # Store hash
        with hashsLock:  # Sending data only on change, therefor no need to check for change
            hashs[receivedObject["_tagId"]] = newHash
        # Write to opc ua by setting the children recursive
        topLevelObject = clientPlc.get_node(
            "ns=" + str(opcUaNs) + ";s=" + opcUaIdPrefix + "." + receivedObject["_tagId"]
        )
        setChildrenRecursive(receivedObject, topLevelObject.get_children())
    except Exception:
        logging.exception("Exception in on_message.")


def setChildrenRecursive(
    pObject, OpcNodes
):  # TODO this should be re-written in the same manner at getting values
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
            elif type(value) is int:
                node.set_value(value, varianttype=ua.VariantType.Int16)
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
mqttClient.on_connect = on_mqtt_connect
mqttClient.on_message = on_received_mqtt_message


def buildNodeTree(pObject, nodeStore, OpcNodes):
    for node in OpcNodes:
        children = node.get_children()
        tagname = getTagname(node)
        if len(children) == 0:
            if tagname.startswith("_"):
                pObject[tagname] = node.get_value()
            else:
                nodeStore[tagname] = node
                pObject[tagname] = node.get_value()
        else:
            nodeStore[tagname] = {}
            pObject[tagname] = {}
            buildNodeTree(pObject[tagname], nodeStore[tagname], children)


def getValuesFromNodes(pObject, nodeStore):
    for tagname, pObje in pObject.items():
        if tagname.startswith("_"):
            continue
        if type(pObje) is dict:
            getValuesFromNodes(pObje, nodeStore[tagname])
        else:
            pObject[tagname] = nodeStore[tagname].get_value()


def getTagname(node):
    path = node.nodeid.Identifier
    position = path.rfind(".")
    return path[position + 1 :]


# Ensure disconnecting on program close
try:
    # Tries to reconnect every 10 seconds
    while True:
        try:
            logging.info("Connecting to Opc.")
            clientPlc.connect()
            if clientPlc is None:
                raise Exception("Opc connection failed")
            logging.info("OPC Connected")
            nodesUnderPrefix = clientPlc.get_node("ns=" + str(opcUaNs) + ";s=" + opcUaIdPrefix)

            logging.info("Connecting to MQTT broker.")
            mqttClient.connect(mqttBroker, mqttPort, 60)
            mqttThread = Thread(target=mqttClient.loop_forever, args=())
            mqttThread.start()
            logging.info("Waiting for MQTT to connect...")
            time.sleep(2)  # MQTT need time to connect

            # Building tag and opc node trees, for better performance on publishing data
            topLevelOpcNodes = nodesUnderPrefix.get_children()
            if len(topLevelOpcNodes) == 0:
                raise Exception("No tags where found")
            for topLevelOpcNode in topLevelOpcNodes:
                tagname = getTagname(topLevelOpcNode)
                tags[tagname] = {}
                tags[tagname]["_timestamp"] = {}
                nodes[tagname] = {}
                buildNodeTree(tags[tagname], nodes[tagname], topLevelOpcNode.get_children())

            # Read data from OPC UA and Publish data to MQTT loop
            while True:
                if cmdPublishCounter > cmdPublishIntervall:
                    cmdPublishCounter = 0
                cmdPublishCounter = cmdPublishCounter + 1

                publishLoopStarttime = time.time()
                # OPC UA Nodes are at start -> need for restart if there are new nodes
                for tagname, pObject in tags.items():
                    getValuesFromNodes(pObject, nodes[tagname])
                    # Building python object, then converting to json before sending
                    # Publishing
                    if mqttPublishPvSuffix in tagname:
                        pObject["_timestamp"] = str(datetime.datetime.now())
                        mqttClient.publish(mqttTopicPublishData, payload=json.dumps(pObject))
                    elif cmdPublishCounter == 1:
                        del pObject["_timestamp"]
                        newHash = hashlib.md5(pObject.__str__().encode("utf-8")).hexdigest()
                        pObject["_timestamp"] = str(datetime.datetime.now())
                        with hashsLock:  # Threadsafe
                            if tagname in hashs:
                                if hashs[tagname] != newHash:
                                    # Publish and save hash
                                    mqttClient.publish(
                                        mqttTopicPublishData, payload=json.dumps(pObject)
                                    )
                                    hashs[tagname] = newHash
                            else:
                                # Tagname does not exist in hashs
                                # Save hash
                                hashs[tagname] = newHash
                                # Publish
                                mqttClient.publish(
                                    mqttTopicPublishData, payload=json.dumps(pObject)
                                )
                logging.warning(
                    "Publish loop used [s]: " + str((time.time() - publishLoopStarttime))
                )
                time.sleep(publishLoopWaitTime)
        except Exception:
            logging.exception("Exception in connection loop.")
        logging.warning("Waiting 10s before trying to reconnect.")
        time.sleep(10)
finally:
    logging.warning("Disconnecting.")
    if clientPlc is not None:
        clientPlc.disconnect()
    mqttClient.disconnect()
logging.warning("OPC UA - MQTT link is shutting down.")
