from SimulationProgram.mqtt_client import MQTTClient
from utils.scheduler import SimpleTaskScheduler
from SimulationProgram.simulatedObjects import Water, RainForcast, WaterDistributionPipes
from SimulationProgram.dbClient import DbClient
import datetime  # Best compatible with mysql
import logging
import time

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.WARNING,
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="simulationprogram.log",
)
sampleTime_s = 5  # DO NOT CHANGE - One sample is in real time 2 hours. 12 samples pr hour.
oneDayIsSimulatedTo_s = 60  # DO NOT CHANGE
simulatedSamplesPerDay = 96  # DO NOT CHANGE

mqttBroker = "broker.hivemq.com"
mqttPort = 1883
mqttTopicSubscribeData = [
    "ba/wago/sim/plc1/plcpub",
    "ba/wago/sim/plc2/plcpub",
    "ba/wago/sim/plc3/plcpub",
]


def mainloop(datetimestamp):
    datetimestamp = datetime.datetime.now()

    """
    # Read data from mqtt
    ValveEmission1Position_Pv = mqtt.getData("ValveEmission1Position_Pv")
    logging.info("ValveEmission1Position %: " + str(ValveEmission1Position_Pv))
    emission_m3_per_s = w.emissionValve_percent_ToFlow_m3_per_s(ValveEmission1Position_Pv)

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
    flowValues, timestamps = waterDistributionPipes.getFlowInPipesSinceLastSample(datetimestamp)
    for i in range(flowValues.__len__()):
        db.insertFlowValuesBatch8DifferentTags(
            ["t0", "t1", "t2", "t3", "t4", "t5", "t6"], flowValues[i], timestamps[i]
        )
    logging.info("Loop used: " + str(datetime.datetime.now() - datetimestamp))


def dbCleanUp(datetimestamp):
    rows = db.deleteDataOlderThan(
        "SignalAnalogHmiPv",
        (datetime.datetime.now() - datetime.timedelta(seconds=oneDayIsSimulatedTo_s * 10)),
    )
    logging.info("SignalAnalogHmiPv Rows deleted: " + str(rows))
    rows = db.deleteDataOlderThan(
        "LeakDetectionHourlyAverage",
        (datetime.datetime.now() - datetime.timedelta(seconds=oneDayIsSimulatedTo_s * 20)),
    )
    logging.info("LeakDetectionHourlyAverage Rows deleted: " + str(rows))
    rows = db.deleteDataOlderThan(
        "LeakDetection120SamplesHourlyAverage",
        (datetime.datetime.now() - datetime.timedelta(seconds=oneDayIsSimulatedTo_s * 30)),
    )
    logging.info("LeakDetection120SamplesHourlyAverage Rows deleted: " + str(rows))


if __name__ == "__main__":
    while True:
        try:
            # Init MQTT
            mqtt = MQTTClient(mqttBroker, mqttPort, mqttTopicSubscribeData)
            mqtt.start()
            time.sleep(5)
            # Init objects
            w = Water(sampleTime_s, oneDayIsSimulatedTo_s, 1000.0, 1000.0, 100.0)
            rain = RainForcast(sampleTime_s, oneDayIsSimulatedTo_s, [1, 1, 8, 8, 1])
            db = DbClient()
            waterDistributionPipes = WaterDistributionPipes(
                sampleTime_s, oneDayIsSimulatedTo_s, simulatedSamplesPerDay
            )
            # Init and start Scheduled task "mainloop"
            s1 = SimpleTaskScheduler(mainloop, sampleTime_s, 0, 0.1)
            s1.start()
            s2 = SimpleTaskScheduler(dbCleanUp, oneDayIsSimulatedTo_s * 3, 1, 0.1)
            s2.start()
            s1.join()
            s2.join()
        except:
            logging.exception("Simulation program exception, restarting in 10 seconds")
        time.sleep(10)
