import paho.mqtt.client as mqtt
import json


class MQTTClient:
    def __init__(self, brokerUrl, brokerPort, brokerKeepALive, subscriptions):
        self.__brokerUrl = brokerUrl
        self.__brokerPort = brokerPort
        self.__brokerKeepALive = brokerKeepALive
        self.__subscriptions = subscriptions
        self.__client = 0
        self.__receivedData = {}

    # The callback for when the client receives a CONNACK response from the server.
    def __on_connect(self, client, userdata, flags, rc):
        print("MQTT broker connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        for subscription in self.__subscriptions:
            self.__client.subscribe(subscription)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))
        self.__receivedData[msg.topic] = msg.payload  # TODO Exception handling

    def getData(self, topic):
        if topic in self.__receivedData:
            return self.__receivedData[topic]
        else:
            return None

    def publish(self, topic, payload, jsonEncoder=None):
        self.__client.publish(topic, payload=payload)

    def disconnect(self):
        self.__client.disconnect()

    def __on_disconnect(self, client, userdata, rc):
        print("MQTT broker disconnected with result code " + str(rc))

    def loopForever(self):
        self.__client = mqtt.Client()
        self.__client.on_connect = self.__on_connect
        self.__client.on_message = self.on_message
        self.__client.on_disconnect = self.__on_disconnect

        self.__client.connect(self.__brokerUrl, self.__brokerPort, self.__brokerKeepALive)
        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        self.__client.loop_forever()
