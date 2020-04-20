from opcua import Client, ua
import paho.mqtt.client as mqtt
from threading import Thread, Lock
from dotenv import load_dotenv
from OPCUA_MQTT_link.utils import getTagname, getNewHash, setTimestamp
import time
import datetime
import json
import hashlib
import os
import logging


def buildNodeTree(pObject, nodeStore, OpcNodes):
    for node in OpcNodes:
        children = node.get_children()
        tagname = getTagname(node)
        if len(children) == 0:
            nodeStore[tagname] = node
            pObject[tagname] = node.get_value()
        else:
            nodeStore[tagname] = {}
            pObject[tagname] = {}
            buildNodeTree(pObject[tagname], nodeStore[tagname], children)


def getValuesFromNodes(pObject, nodeStore):
    for tagname, pObje in pObject.items():
        if type(pObje) is dict:
            getValuesFromNodes(pObje, nodeStore[tagname])
        else:
            pObject[tagname] = nodeStore[tagname].get_value()


def setValuesToNodes(pObject, nodeStore):
    for tagname, pObje in pObject.items():
        if type(pObje) is dict:
            setValuesToNodes(pObje, nodeStore[tagname])
        else:
            try:
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
                    raise Exception("HMI: Type not found")
            except:
                logging.exception("HMI: Exception in setValuesToNodes")


def on_mqtt_connect(client, userdata, flags, rc):
    logging.warning("HMI: MQTT Connected with result code " + str(rc))
    for topic in mqttTopicSubscribeData:
        logging.warning("HMI: MQTT subscribring to: " + topic)
        client.subscribe(topic)


def on_received_mqtt_message(client, userdata, msg):
    global hashsLock, hashs, nodes, tags
    try:
        receivedObject = json.loads(str(msg.payload, encoding="utf-8"))
        tagname = receivedObject["_tagId"]
        # Generate new hash
        # Timestamp will always change and are therefore excluded
        newHash = getNewHash(receivedObject)
        # Store hash
        with hashsLock:  # Sending data only on change, therefore no need to check for change
            hashs[receivedObject["_tagId"]] = newHash
        # Write to opc ua by setting the children recursive
        setValuesToNodes(receivedObject, nodes[tagname])
    except Exception:
        logging.exception(
            "HMI: Exception in on_message. Topic: "
            + msg.topic
            + " content: "
            + str(msg.payload, encoding="utf-8")
        )


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
        logging.warning("HMI: Unregistered object: " + pObject["_tagId"])
    else:
        raise Exception("HMI: Unknown owner of object: " + pObject["_tagId"])


if __name__ == "__main__":
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
    opcUaIdCounter = os.getenv("OPC_UA_ID_STATUS_COUNTER")
    opcUaIdLastRun = os.getenv("OPC_UA_ID_STATUS_LAST_RUN")
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
    logging.warning(
        "HMI: Evn: OpcUaServer: "
        + opcUaServer
        + ", OpcUaIdPrefix"
        + opcUaIdPrefix
        + ", MqttBroker: "
        + mqttBroker
    )
    # OPC UA
    clientPlc = Client("opc.tcp://" + opcUaServer + ":4840", timeout=3)
    clientPlc.set_user(opcUaServerUsername)
    clientPlc.set_password(opcUaServerPassword)

    # MQTT
    mqttClient = mqtt.Client()
    mqttClient.on_connect = on_mqtt_connect
    mqttClient.on_message = on_received_mqtt_message
    # Ensure disconnecting on program close
    try:
        # Tries to reconnect every 10 seconds
        while True:
            try:
                logging.warning("HMI: Connecting to Opc.")
                clientPlc.connect()
                if clientPlc is None:
                    raise Exception("HMI: Opc connection failed")
                logging.warning("HMI: OPC Connected")
                nodesUnderPrefix = clientPlc.get_node("ns=" + str(opcUaNs) + ";s=" + opcUaIdPrefix)

                # Building tag and opc node trees, for better performance on publishing data
                topLevelOpcNodes = nodesUnderPrefix.get_children()
                if len(topLevelOpcNodes) == 0:
                    raise Exception("HMI: No tags where found")
                for topLevelOpcNode in topLevelOpcNodes:
                    tagname = getTagname(topLevelOpcNode)
                    tags[tagname] = {}
                    nodes[tagname] = {}
                    buildNodeTree(tags[tagname], nodes[tagname], topLevelOpcNode.get_children())

                logging.warning("HMI: Connecting to MQTT broker.")
                mqttClient.connect(mqttBroker, mqttPort, 60)
                mqttThread = Thread(target=mqttClient.loop_forever, args=())
                mqttThread.start()
                logging.warning("HMI: Waiting 2s for MQTT to connect...")
                time.sleep(2)  # MQTT need time to connect

                loopCounter = 0
                # Read data from OPC UA and Publish data to MQTT loop
                while True:
                    # OPC UA Nodes are initialized each loop -> no need for restart if there are new nodes
                    publishLoopStarttime = time.time()
                    loopCounter = loopCounter + 1
                    for tagname, pObject in tags.items():
                        # Building python object, then converting to json before sending
                        if "_timestamp" in pObject:
                            del pObject["_timestamp"]
                        getValuesFromNodes(pObject, nodes[tagname])
                        # Publishing, HMI does not publish process values
                        if mqttPublishPvSuffix in tagname:
                            continue
                        else:
                            newHash = getNewHash(pObject)
                            setTimestamp(pObject)
                            # Missing data from plc -> publish to get
                            if tagname in hashs and pObject["_type"] != "":
                                if hashs[tagname] != newHash:
                                    # Publish and save hash
                                    logging.warning("HMI: HMI is sending: " + tagname)
                                    with hashsLock:
                                        hashs[tagname] = newHash
                                    publish(pObject)
                            else:
                                # Tagname does not exist in hashs
                                # Save hash and publish
                                logging.warning("HMI: HMI is sending: " + tagname)
                                with hashsLock:
                                    hashs[tagname] = newHash
                                publish(pObject)
                    logging.warning(
                        "Publish loop used [s]: " + str((time.time() - publishLoopStarttime))
                    )
                    node = clientPlc.get_node("ns=" + str(opcUaNs) + ";s=" + opcUaIdCounter)
                    node.set_value(loopCounter, varianttype=ua.VariantType.Int16)
                    node = clientPlc.get_node("ns=" + str(opcUaNs) + ";s=" + opcUaIdLastRun)
                    node.set_value(time.ctime())
                    time.sleep(publisLoopWaitTime)
            except Exception:
                logging.exception(
                    "HMI: Exception in connection loop. Trying to reconnect in 10 seconds"
                )
            time.sleep(10)
    finally:
        if clientPlc is not None:
            clientPlc.disconnect()
        mqttClient.disconnect()
    logging.warning("HMI: OPC UA - MQTT link is shutting down.")
