from opcua import Client, ua
import paho.mqtt.client as mqtt
from threading import Thread
import time
import json
import hashlib


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("ba/wago/data/test/motta/#")


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


clientPlc = Client("opc.tcp://192.168.0.15:4840")
clientPlc.set_user("admin")
clientPlc.set_password("wago")
ns = 4
HmiId = "|var|WAGO 750-8214 PFC200 G2 2ETH RS CAN.PFCx00_SmartCoupler.HMI"
variables = {}
nodes = {}
hashs = {}


def getChildrenRecursive(jsonObject, OpcNodes):
    # children = OpcNode.get_children()
    for node in OpcNodes:
        children = node.get_children()
        if len(children) == 0:
            path = node.nodeid.Identifier
            position = path.rfind(".")
            tagname = path[position + 1 :]
            jsonObject[tagname] = node.get_value()
        else:
            path = node.nodeid.Identifier
            position = path.rfind(".")
            tagname = path[position + 1 :]
            jsonObject[tagname] = {}
            getChildrenRecursive(jsonObject[tagname], children)


try:
    # Init
    clientPlc.connect()
    HMITags = clientPlc.get_node("ns=" + str(ns) + ";s=" + HmiId)
    mqttClient = mqtt.Client()
    mqttClient.on_connect = on_connect
    mqttClient.on_message = on_message
    mqttClient.connect("broker.hivemq.com", 1883, 60)
    mqttThread = Thread(target=mqttClient.loop_forever, args=())
    mqttThread.start()
    time.sleep(2)  # Time to connect mqtt

    # Loop
    while True:
        topLevelObjects = HMITags.get_children()
        if len(topLevelObjects) == 0:
            raise Exception("No tags where found")
        for Object in topLevelObjects:
            path = Object.nodeid.Identifier
            position = path.rfind(".")
            tagname = path[position + 1 :]
            variables[tagname] = {}
            getChildrenRecursive(variables[tagname], Object.get_children())
            # Publishing
            jsondump = json.dumps(variables[tagname])
            if "Pv" in tagname:
                mqttClient.publish("ba/wago/opcua/test", payload=jsondump)
            else:
                # Hash
                newValueHash = hashlib.md5(jsondump.encode("utf-8")).hexdigest()
                if tagname in hashs:
                    # Compare
                    if hashs[tagname] != newValueHash:
                        mqttClient.publish("ba/wago/opcua/test", payload=jsondump)
                        # Publish and save hash
                        hashs[tagname] = newValueHash
                    # Or nothing
                else:
                    # Tagname does not exist in hashs
                    # Save hash
                    hashs[tagname] = newValueHash
                    # Publish
                    mqttClient.publish("ba/wago/opcua/test", payload=jsondump)
        time.sleep(10)


except Exception as e:
    print(e)
finally:
    clientPlc.disconnect()
    mqttClient.disconnect()
