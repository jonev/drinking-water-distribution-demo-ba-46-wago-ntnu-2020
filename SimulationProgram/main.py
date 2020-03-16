from mqtt_client import MQTTClient
from scheduler import SimpleTaskScheduler
from simulatedObjects import Water, RainForcast, WaterDistributionPipes
from DbClient import DbClient
import time
import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="simulationprogram.log",
)
sampleTime_s = 5  # DO NOT CHANGE - One sample is in real time 2 hours. 12 samples pr hour.
oneDayIsSimulatedTo_s = 60  # DO NOT CHANGE

mqttBroker = "broker.hivemq.com"
mqttPort = 1883
mqttTopicSubscribeData = [
    "ba/wago/sim/plc1/plcpub",
    "ba/wago/sim/plc2/plcpub",
    "ba/wago/sim/plc3/plcpub",
]


def mainloop():
    timestamp = time.time()
    """
    # Read data from mqtt
    ValveEmission1Position_Pv = mqtt.getData("ValveEmission1Position_Pv")
    logging.info("ValveEmission1Position %: " + str(ValveEmission1Position_Pv))
    emission_m3_per_s = w.emmissionValve_percent_ToFlow_m3_per_s(ValveEmission1Position_Pv)

    # Calculating new current volume
    rain.calculateRain()
    rain_m = rain.getRain_m()
    rainforcast = rain.getForcast()
    w.addCurrentRain_m_ToCurrentVolume(rain_m, oneDayIsSimulatedTo_s)
    w.addInflowFromRivers()
    w.setWantedEmission_m3_per_s(emission_m3_per_s)

    # Collecting data and writing to mqtt
    waterLevel_m = w.getWaterLevel_m()
    waterLevel_percent = w.getWaterLevel_percent()
    mqtt.publishPlc3(
        {
            "WaterLevel_Pv": waterLevel_percent,
            "EmissionFlow_Pv": emission_m3_per_s,
            "RainForcast": rainforcast.__str__(),  # This is a fix to be able to parse the data in the PLC
        }
    )
    logging.info("Waterlevel m: " + str(waterLevel_m))
    logging.info("Emission m3/s: " + str(emission_m3_per_s))
    logging.info("Forcast: " + str(rainforcast) + " Rain: " + str(rain_m))
    """
    waterDistributionPipes.calculateFlowInPipesNow()
    print("Flow in pipes: " + str(waterDistributionPipes.getFlowInPipes()))
    flowValues = waterDistributionPipes.calculateFlowInPipesSinceLastSample()
    for flow in flowValues:
        print("Flow since last sample: " + str(flow))


if __name__ == "__main__":
    # Init MQTT
    mqtt = MQTTClient(mqttBroker, mqttPort, mqttTopicSubscribeData)
    mqtt.start()
    time.sleep(5)
    # Init objects
    w = Water(sampleTime_s, oneDayIsSimulatedTo_s)
    rain = RainForcast(sampleTime_s, oneDayIsSimulatedTo_s, [1, 1, 8, 8, 1])
    db = DbClient()
    waterDistributionPipes = WaterDistributionPipes(sampleTime_s, oneDayIsSimulatedTo_s)
    # Init and start Scheduled task "mainloop"
    s = SimpleTaskScheduler(mainloop, sampleTime_s, 0.1)
    s.start()
    s.join()
