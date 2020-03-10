from plclib.mqtt_client import MQTTClient
from threading import Thread
import json

mqtt = MQTTClient("broker.hivemq.com", 1883, 60, ["wago/ba/sim/#"])
mqttThread = Thread(target=mqtt.loopForever, args=())
mqttThread.start()
time.sleep(2)

dict_ = {
    "dayCounter": self.day_counter,
}
mqtt.publish("wago/ba/sim/out/PLS2", json.dumps(dict_))
time.sleep(1)
