# import paho.mqtt.client as mqtt
from plclib.mqtt_client import MQTTClient
import json

mqttBroker = "broker.hivemq.com"
mqttPort = 1883
mqttTopic = "wago/ba/sim/out/PLS2"


def on_connect(client, userdata, flags, rc):
    print("MQTT Connected with result code " + str(rc))
    client.subscribe(mqttTopic)


def on_message(client, userdata, msg):
    print(msg.topic + str(msg.payload))
    receivedObject = json.loads(str(msg.payload, encoding="utf-8"))
    print(receivedObject)


mqttClient = mqtt.Client()
mqttClient.connect(mqttBroker, mqttPort, 60)
mqttClient.on_connect = on_connect
mqttClient.on_message = on_message
mqttClient.loop_forever()
