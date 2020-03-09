import paho.mqtt.client as mqtt
from pymongo import MongoClient
import json
import datetime

## MQTT
mqttBroker = "broker.hivemq.com"
mqttPort = 1883
mqttTopic = "ba/wago/opcua/test/plcpub"
# Mongodb
client = MongoClient(host="mongo", port=27017)
db = client.testdb


def on_connect(client, userdata, flags, rc):
    print("MQTT Connected with result code " + str(rc))
    client.subscribe(mqttTopic)


def on_message(client, userdata, msg):
    print(msg.topic + str(msg.payload))
    try:
        receivedObject = json.loads(str(msg.payload, encoding="utf-8"))
        receivedObject["_timestamp"] = datetime.datetime.now()
        result = db.testtable.insert_one(receivedObject)
        print(result)
    except Exception as e:
        print(e)


mqttClient = mqtt.Client()
mqttClient.connect(mqttBroker, mqttPort, 60)
mqttClient.on_connect = on_connect
mqttClient.on_message = on_message
mqttClient.loop_forever()
