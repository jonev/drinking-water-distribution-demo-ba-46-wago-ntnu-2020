from mqtt_client import MQTTClient
from scheduler import SimpleTaskScheduler
import time
from water import Water
import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.WARNING,
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="simulationprogram.log",
)
sampleTime_s = 5.0
oneDayIsSimulatedTo_s = 25.0

mqttBroker = "broker.hivemq.com"
mqttPort = 1883
mqttTopicSubscribeData = [
    "ba/wago/sim/plc1/plcpub",
    "ba/wago/sim/plc2/plcpub",
    "ba/wago/sim/plc3/plcpub",
]


def mainloop():
    # Read data from mqtt
    ValveEmission1Position_Pv = mqtt.getData("ValveEmission1Position_Pv")
    logging.info("ValveEmission1Position %: " + str(ValveEmission1Position_Pv))

    w.addCurrentRain_m_ToCurrentVolume(0.040, oneDayIsSimulatedTo_s)  # 40mm per day

    emission_m3_per_s = w.emmissionValve_percent_ToFlow_m3_per_s(ValveEmission1Position_Pv)
    w.setWantedEmission_m3_per_s(emission_m3_per_s)

    waterLevel_m = w.getWaterLevel_m()

    mqtt.publishPlc3({"WaterLevel_Pv": waterLevel_m, "EmissionFlow_Pv": emission_m3_per_s})

    logging.info("Waterlevel m: " + str(waterLevel_m))
    logging.info("Emission m3/s: " + str(emission_m3_per_s))


if __name__ == "__main__":
    mqtt = MQTTClient(mqttBroker, mqttPort, mqttTopicSubscribeData)
    mqtt.start()
    time.sleep(5)
    w = Water(sampleTime_s, oneDayIsSimulatedTo_s)
    s = SimpleTaskScheduler(mainloop, sampleTime_s, 0.1)
    s.start()
    s.join()
