from utils.scheduler import SimpleTaskScheduler
from LeakDetection.dbLeakDetectionClient import DbLeakDetectionClient
from LeakDetection.divcalculations import DivCalculations
import datetime  # Best compatible with mysql
import logging
import time
import queue

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

sampleTime_s = 5  # DO NOT CHANGE - One sample is in real time 2 hours. 12 samples pr hour.
oneDayIsSimulatedTo_s = 60  # DO NOT CHANGE
oneHour_s = oneDayIsSimulatedTo_s / 24
simulatedSamplesPerDay = 96  # DO NOT CHANGE


def updatePoints(diff, limit, points, queue):
    if diff > limit:
        points = points + 1
        queue.put(1)
    else:
        queue.put(0)
    removedItem = queue.get()
    if removedItem == 1:
        points = points - 1
    return points


def calculateHourlyAverageValues(datetimestamp):
    global pointsOver10, pointsOver20, pointsOver30, queuePointsOver10, queuePointsOver20, queuePointsOver30
    try:
        # print("Timestamp run: " + str(datetimestamp))
        timetaking = datetime.datetime.now()
        datetimestamp = datetimestamp - datetime.timedelta(seconds=5)
        # print("Timestamp this run: " + str(datetimestamp))
        start = datetimestamp - datetime.timedelta(seconds=oneHour_s)
        end = datetimestamp
        values = dbClient.getValuesBetweenTimestamps("SignalAnalogHmiPv", start, end, "t0",)
        # Skipping values of 0.00
        avgHour = DivCalculations.avgValue(values, 4)
        if avgHour != 0.00:
            dbClient.pushValueOnTimestamp("LeakDetectionHourlyAverage", start, "t0", avgHour)

        values120SamplesHourlyAverages = dbClient.getAverageHourValues(
            "LeakDetectionHourlyAverage",
            "t0",
            (start.second - 0.1) % 60,
            (end.second + 0.1) % 60,
            5,
        )
        avg120samples = DivCalculations.avgValue(values120SamplesHourlyAverages, 4)
        if avg120samples != 0.00:
            dbClient.pushValueOnTimestamp(
                "LeakDetection120SamplesHourlyAverage", start, "t0", avg120samples
            )

        # Calculating points over limit
        if avg120samples != 0.00:
            diffNowInPercent = avgHour / avg120samples
            pointsOver10 = updatePoints(diffNowInPercent, 1.10, pointsOver10, queuePointsOver10)
            pointsOver20 = updatePoints(diffNowInPercent, 1.20, pointsOver20, queuePointsOver20)
            pointsOver30 = updatePoints(diffNowInPercent, 1.30, pointsOver30, queuePointsOver30)
            dbClient.pushPointsOnTimestamp(
                "LeakDetectionAlarmPoints", start, "t0", pointsOver10, pointsOver20, pointsOver30
            )

        logging.info(
            "Ran at: "
            + str(datetimestamp)
            + ", Loop used: "
            + str(datetime.datetime.now() - timetaking)
        )
    except:
        logging.exception("Exception in calculateHourlyAverageValues")


if __name__ == "__main__":
    while True:
        try:
            logging.info("Starting in __main__")
            # Init db
            dbClient = DbLeakDetectionClient()
            dbClient.connectHost("db", "root", "example")
            dbClient.createDatabase("processvalues")
            dbClient.connectDatabase("db", "root", "example", "processvalues")

            dbClient.createTable(
                "SignalAnalogHmiPv",
                "(id INT AUTO_INCREMENT PRIMARY KEY, _tagId VARCHAR(124), metric VARCHAR(3), timestamp DATETIME(6), Output_Pv FLOAT)",
            )
            dbClient.createTable(
                "LeakDetectionHourlyAverage",
                "(id INT AUTO_INCREMENT PRIMARY KEY, _tagId VARCHAR(124), metric VARCHAR(3), timestamp DATETIME(6), value FLOAT)",
            )
            dbClient.createTable(
                "LeakDetection120SamplesHourlyAverage",
                "(id INT AUTO_INCREMENT PRIMARY KEY, _tagId VARCHAR(124), metric VARCHAR(3), timestamp DATETIME(6), value FLOAT)",
            )
            dbClient.createTable(
                "LeakDetectionAlarmPoints",
                "(id INT AUTO_INCREMENT PRIMARY KEY, _tagId VARCHAR(124), timestamp DATETIME(6), pointsOver10 INT, pointsOver20 INT, pointsOver30 INT)",
            )
            # Queues
            queuePointsOver10 = queue.Queue()
            queuePointsOver20 = queue.Queue()
            queuePointsOver30 = queue.Queue()
            for i in range(24):
                queuePointsOver10.put(0)
                queuePointsOver20.put(0)
                queuePointsOver30.put(0)
            pointsOver10 = 0
            pointsOver20 = 0
            pointsOver30 = 0

            # Init and start Scheduled task "mainloop"
            s = SimpleTaskScheduler(calculateHourlyAverageValues, oneHour_s, 0, 0.1)
            s.start()
            s.join()
        except:
            logging.exception("Leak detection exception, restarting in 10 seconds")
        time.sleep(10)
