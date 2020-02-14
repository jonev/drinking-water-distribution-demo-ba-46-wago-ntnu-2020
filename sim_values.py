from plclib.mqtt_client import MQTTClient

mqtt = MQTTClient("broker.hivemq.com", 1883, 60, ["wago/ba/sim/out"])

mqtt.publish("wago/ba/sim", "Hei fra Python")
mqtt.loopForever()

