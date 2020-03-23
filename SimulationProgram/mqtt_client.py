import paho.mqtt.client as mqtt
from threading import Thread, Lock
from enum import Enum
import time
import json
import logging


class PublishTopic(Enum):
    PLC1 = "ba/wago/sim/plc1/plcsub"
    PLC2 = "ba/wago/sim/plc2/plcsub"
    PLC3 = "ba/wago/sim/plc3/plcsub"
    HMI = "ba/wago/sim/hmi/hmisub"
    INFO = "ba/wago/sim/info"


class MQTTClient:
    def __init__(self, broker, port, subscribeTopics):
        self.__broker = broker
        self.__port = port
        self.__subscribeTopics = subscribeTopics
        self.__client = mqtt.Client()
        self.__client.on_connect = self.__on_connect
        self.__client.on_message = self.__on_message
        self.__receivedData = {}
        self.__receivedDataLock = Lock()

    def __on_connect(self, client, userdata, flags, rc):
        logging.info("Connected with result code " + str(rc))
        for t in self.__subscribeTopics:
            client.subscribe(t)

    def __on_message(self, client, userdata, msg):
        # print(msg.topic + " " + str(msg.payload))
        receivedObject = json.loads(str(msg.payload, encoding="utf-8"))
        with self.__receivedDataLock:
            for key, value in receivedObject.items():
                self.__receivedData[key] = value

    def getData(self, tagname):
        with self.__receivedDataLock:
            if tagname in self.__receivedData:
                return self.__receivedData[tagname]
            else:
                return 0

    def __publish(self, topic, pObject):
        self.__client.publish(topic, payload=json.dumps(pObject))

    def publishPlc1(self, pObject):
        self.__publish(PublishTopic.PLC1.value, pObject=pObject)

    def publishPlc2(self, pObject):
        self.__publish(PublishTopic.PLC2.value, pObject=pObject)

    def publishPlc3(self, pObject):
        self.__publish(PublishTopic.PLC3.value, pObject=pObject)

    def publishHmi(self, pObject):
        self.__publish(PublishTopic.HMI.value, pObject=pObject)

    def start(self):
        self.__client.connect(self.__broker, self.__port, 60)
        self.__client.publish(PublishTopic.INFO.value, payload="Simulation program MQTT staring")
        self.__mqttThread = Thread(target=self.__client.loop_forever, args=())
        self.__mqttThread.start()
