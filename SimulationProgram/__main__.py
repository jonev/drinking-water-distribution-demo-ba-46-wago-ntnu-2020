from SimulationProgram.mqtt_client import MQTTClient
from utils.scheduler import SimpleTaskScheduler
from SimulationProgram.simulatedObjects import Water, RainForcast, WaterDistributionPipes
from SimulationProgram.DbClient import DbClient

from SimulationProgram.yrForecastToHmi import YrForecastToHmi
from SimulationProgram.battery_level import BatteryLevel
import datetime  # Best compatible with mysql
import logging
import time
import json

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)
sampleTime_s = 5  # DO NOT CHANGE - One sample is in real time 2 hours. 12 samples pr hour.
oneDayIsSimulatedTo_s = 60  # DO NOT CHANGE
simulatedSamplesPerDay = 96  # DO NOT CHANGE

version = "0.0.17"
mqttBroker = "broker.hivemq.com"
mqttPort = 1883
mqttTopicSubscribeData = [
    "ba/wago/sim/plc1/plcpub",
    "ba/wago/sim/plc2/plcpub",
    "ba/wago/sim/plc3/plcpub",
]


def mainloop(datetimestamp):
    timetaking = datetime.datetime.now()

    # Simulation Water and rain
    ## Read data from mqtt
    ValveEmission1Position_Pv = mqtt.getData("ValveEmission1Position_Pv")
    emission_m3_per_s = w.emissionValve_percent_ToFlow_m3_per_s(ValveEmission1Position_Pv)

    ## Calculating new current volume
    rainObj.calculateRain()
    rain_m = rainObj.getRain_m()
    rainforcast = rainObj.getForcast()
    w.addCurrentRain_m_ToCurrentVolume(rain_m, oneDayIsSimulatedTo_s)
    w.addInflowFromRivers()
    w.setWantedEmission_m3_per_s(emission_m3_per_s)

    ## Collecting data and writing to mqtt
    waterLevel_m = w.getWaterLevel_m()
    # waterLevel_percent = w.getWaterLevel_percent()
    mqtt.publishPlc3(
        {
            "WaterLevel_Pv": waterLevel_m,
            "EmissionFlow_Pv": emission_m3_per_s,
            "RainForcast": rainforcast.__str__(),  # This is a fix to be able to parse the data in the PLC
        }
    )
    logging.info(
        "Waterlevel m: "
        + str(waterLevel_m)
        + ", Emission m3/s: "
        + str(emission_m3_per_s)
        + ", Forcast: "
        + str(rainforcast)
        + ", Rain: "
        + str(rain_m)
    )

    # Simulation for leakdetection - the order is important
    waterDistributionPipes.calculateFlowInPipesNow()
    nowValueFlows = waterDistributionPipes.getFlowInPipes()
    nowValueFlowsDict = {
        "FT01": round(nowValueFlows[0], 2),
        "FT02": round(nowValueFlows[1], 2),
        "FT03": round(nowValueFlows[2], 2),
        "FT04": round(nowValueFlows[3], 2),
        "FT05": round(nowValueFlows[4], 2),
        "FT06": round(nowValueFlows[5], 2),
        "FT07": round(nowValueFlows[6], 2),
    }

    flowValues, timestamps = waterDistributionPipes.getFlowInPipesSinceLastSample(datetimestamp)
    for i in range(flowValues.__len__()):
        db.insertFlowValuesBatch8DifferentTags(
            [
                "WaterFlowFT01_Pv",
                "WaterFlowFT02_Pv",
                "WaterFlowFT03_Pv",
                "WaterFlowFT04_Pv",
                "WaterFlowFT05_Pv",
                "WaterFlowFT06_Pv",
                "WaterFlowFT07_Pv",
            ],
            flowValues[i],
            timestamps[i],
        )

    # Battery levels
    nowBatteryLevels = batteryLevels.getBatteryLevelValues()
    nowValueFlowsDict.update(nowBatteryLevels)
    mqtt.publishPlc1(nowValueFlowsDict)
    logging.info(
        "Ran at: "
        + str(datetimestamp)
        + ", Loop used: "
        + str(datetime.datetime.now() - timetaking)
    )


def dbCleanUp(datetimestamp):
    logging.info("Starting dbCleanUp")
    rows = db.deleteDataOlderThan(
        "SignalAnalogHmiPv",
        (
            datetime.datetime.now() - datetime.timedelta(seconds=oneDayIsSimulatedTo_s * 10)
        ),  # 10 Days
    )
    logging.info("SignalAnalogHmiPv Rows deleted: " + str(rows))
    rows = db.deleteDataOlderThan(
        "LeakDetectionHourlyAverage",
        (
            datetime.datetime.now() - datetime.timedelta(seconds=oneDayIsSimulatedTo_s * 20)
        ),  # 20 Days
    )
    logging.info("LeakDetectionHourlyAverage Rows deleted: " + str(rows))
    rows = db.deleteDataOlderThan(
        "LeakDetection120SamplesHourlyAverage",
        (
            datetime.datetime.now() - datetime.timedelta(seconds=oneDayIsSimulatedTo_s * 30)
        ),  # 30 Days
    )
    logging.info("LeakDetection120SamplesHourlyAverage Rows deleted: " + str(rows))


def requestForcastAndSendToHmi(datetimestamp):
    try:  # Dependent on 3. party solution, therefore -> try - except
        logging.info("Starting requestForcastAndSendToHmi")
        forecastToSend = forcastToHmi.getForecast()
        logging.info("Publishing forcast from yr to HMI: " + str(forecastToSend))
        mqtt.publishHmi(forecastToSend)
    except:
        logging.exception("Exception in requestForcastAndSendToHmi")


if __name__ == "__main__":
    while True:
        s1 = SimpleTaskScheduler(mainloop, sampleTime_s, 0, 0.1)
        s2 = SimpleTaskScheduler(dbCleanUp, oneDayIsSimulatedTo_s * 3, 1, 0.1)
        s3 = SimpleTaskScheduler(requestForcastAndSendToHmi, 60.0, 0.0, 5.0)

        try:
            logging.info("Starting Simulation in __main__ version: " + version)
            logging.info("Waiting for db to start - 30 seconds")
            time.sleep(30)
            # Init MQTT
            mqtt = MQTTClient(mqttBroker, mqttPort, mqttTopicSubscribeData)
            mqtt.start()
            logging.info("Waiting 5 seconds for MQTT to connect")
            time.sleep(5)
            # Init objects
            w = Water(sampleTime_s, oneDayIsSimulatedTo_s, 22000.0, 25.0)
            rainObj = RainForcast(sampleTime_s, oneDayIsSimulatedTo_s, [0, 0, 0.5, 0.5, 0])
            logging.info("Connecting to db")
            db = DbClient()

            waterDistributionPipes = WaterDistributionPipes(
                sampleTime_s, oneDayIsSimulatedTo_s, simulatedSamplesPerDay
            )

            forcastToHmi = YrForecastToHmi()
            batteryLevels = BatteryLevel()
            # Init and start Scheduled task "mainloop"
            waitTimeBeforeStart = 59 - (time.time() % 60)
            logging.info("Waiting for a new day befor starting: " + str(waitTimeBeforeStart) + " s")
            time.sleep(waitTimeBeforeStart)
            logging.info("Starting periodic tasks: " + str(time.time()))
            s1.start()
            s2.start()
            s3.start()

            logging.info("Periodic tasks started")
            s1.join()
            s2.join()
            s3.join()
        except:
            logging.exception("Simulation program exception, restarting in 10 seconds")
        finally:
            logging.info("Stopping periodic tasks")
            if s1 is not None:
                s1.stop()
                s1.join()
                logging.info("mainloop stopped")
            if s2 is not None:
                s2.stop()
                s2.join()
                logging.info("dbCleanUp stopped")
            if s3 is not None:
                s3.stop()
                s3.join()
                logging.info("requestForcastAndSendToHmi stopped")
        time.sleep(10)
