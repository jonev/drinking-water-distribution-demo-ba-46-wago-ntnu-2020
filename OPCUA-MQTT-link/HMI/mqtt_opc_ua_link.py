from opcua import Client, ua
import paho.mqtt.client as mqtt
from threading import Thread, Lock
from dotenv import load_dotenv
import time
import datetime
import json
import hashlib
import os
import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.WARNING,
    datefmt="%Y-%m-%d %H:%M:%S",
)

load_dotenv()

# Global variables
tags = {}
nodes = {}
hashs = {}  # Storing a hash of the object to be able to compare two objects fast
hashsLock = Lock()  # hashs are used in multiple threads
publisLoopWaitTime = int(os.getenv("WAIT_TIME"))  # For testing
## Opc UA
opcUaServer = os.getenv("OPC_UA_SERVER")  # Host of docker
opcUaServerUsername = os.getenv("OPC_UA_SERVER_USERNAME")
opcUaServerPassword = os.getenv("OPC_UA_SERVER_PASSWORD")
opcUaNs = int(os.getenv("OPC_UA_NS"))  # Address
opcUaIdPrefix = os.getenv("OPC_UA_ID_PREFIX")
## MQTT
mqttBroker = os.getenv("MQTT_BROKER")
mqttPort = int(os.getenv("MQTT_PORT"))
mqttTopicPublishData = [
    "ba/wago/opcua/plc1/plcsub",
    "ba/wago/opcua/plc2/plcsub",
    "ba/wago/opcua/plc3/plcsub",
]
mqttTopicSubscribeData = [
    "ba/wago/opcua/plc1/plcpub",
    "ba/wago/opcua/plc2/plcpub",
    "ba/wago/opcua/plc3/plcpub",
]
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
    for topic in mqttTopicSubscribeData:
        logging.info("MQTT subscribring to: " + topic)
        client.subscribe(topic)


def on_received_mqtt_message(client, userdata, msg):
    global hashsLock
    try:
        receivedObject = json.loads(str(msg.payload, encoding="utf-8"))
        tagname = receivedObject["_tagId"]
        # Generate new hash
        # Timestamp will always change and are therefore excluded
        del receivedObject["_timestamp"]
        newHash = hashlib.md5(receivedObject.__str__().encode("utf-8")).hexdigest()
        # Store hash
        with hashsLock:  # Sending data only on change, therefore no need to check for change
            hashs[receivedObject["_tagId"]] = newHash
        # Write to opc ua by setting the children recursive
        setValuesToNodes(receivedObject, nodes[tagname])
    except Exception:
        logging.exception("Exception in on_message.")


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


def setValuesToNodes(pObject, nodeStore):
    for tagname, pObje in pObject.items():
        if tagname.startswith("_"):
            continue
        if type(pObje) is dict:
            setValuesToNodes(pObje, nodeStore[tagname])
        else:
            value = pObje
            node = nodeStore[tagname]
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


def getTagname(node):
    path = node.nodeid.Identifier
    position = path.rfind(".")
    return path[position + 1 :]


def publish(pObject):
    if pObject["_owner"] == "plc1":
        mqttClient.publish(mqttTopicPublishData[0], payload=json.dumps(pObject))
    elif pObject["_owner"] == "plc2":
        mqttClient.publish(mqttTopicPublishData[1], payload=json.dumps(pObject))
    elif pObject["_owner"] == "plc3":
        mqttClient.publish(mqttTopicPublishData[2], payload=json.dumps(pObject))
    elif pObject["_owner"] == "all":
        mqttClient.publish(mqttTopicPublishData[0], payload=json.dumps(pObject))
        mqttClient.publish(mqttTopicPublishData[1], payload=json.dumps(pObject))
        mqttClient.publish(mqttTopicPublishData[2], payload=json.dumps(pObject))
    elif pObject["_owner"] == "":
        logging.warning("Unregistered object: " + pObject["_tagId"])
    else:
        raise Exception("Unknown owner of object: " + pObject["_tagId"])


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

            logging.info("Connecting to MQTT broker.")
            mqttClient.connect(mqttBroker, mqttPort, 60)
            mqttThread = Thread(target=mqttClient.loop_forever, args=())
            mqttThread.start()
            logging.info("Waiting 2s for MQTT to connect...")
            time.sleep(2)  # MQTT need time to connect

            # Read data from OPC UA and Publish data to MQTT loop
            while True:
                # OPC UA Nodes are initialized each loop -> no need for restart if there are new nodes
                publishLoopStarttime = time.time()

                for tagname, pObject in tags.items():
                    # Building python object, then converting to json before sending
                    getValuesFromNodes(pObject, nodes[tagname])
                    # Publishing, HMI does not publish process values
                    if mqttPublishPvSuffix in tagname:
                        continue
                    else:
                        del pObject["_timestamp"]
                        newHash = hashlib.md5(pObject.__str__().encode("utf-8")).hexdigest()
                        pObject["_timestamp"] = str(datetime.datetime.now())
                        with hashsLock:  # Threadsafe
                            # Missing data from plc -> publish to get
                            if tagname in hashs and pObject["_type"] != "":
                                if hashs[tagname] != newHash:
                                    # Publish and save hash
                                    logging.warning("HMI is requesting: " + tagname)
                                    hashs[tagname] = newHash
                                    publish(pObject)
                            else:
                                # Tagname does not exist in hashs
                                # Save hash and publish
                                logging.warning("HMI is requesting: " + tagname)
                                hashs[tagname] = newHash
                                publish(pObject)
                logging.warning(
                    "Publish loop used [s]: " + str((time.time() - publishLoopStarttime))
                )
                time.sleep(publisLoopWaitTime)
        except Exception:
            logging.exception("Exception in connection loop.")
        time.sleep(10)
finally:
    if clientPlc is not None:
        clientPlc.disconnect()
    mqttClient.disconnect()
logging.warning("OPC UA - MQTT link is shutting down.")
