from utils.scheduler import SimpleTaskScheduler
from LeakDetection.dbLeakDetectionClient import DbLeakDetectionClient
from LeakDetection.divcalculations import DivCalculations
import datetime  # Best compatible with mysql
import logging
import time

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

sampleTime_s = 5  # DO NOT CHANGE - One sample is in real time 2 hours. 12 samples pr hour.
oneDayIsSimulatedTo_s = 60  # DO NOT CHANGE
oneHour_s = oneDayIsSimulatedTo_s / 24
simulatedSamplesPerDay = 96  # DO NOT CHANGE


def calculateHourlyAverageValues(datetimestamp):
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
        if (avgHour != 0.0) and (avg120samples != 0.00):
            dbClient.pushValueOnTimestamp(
                "LeakDetectionDeviationHourAnd120SamplesHourlyAverage",
                start,
                "t0",
                (avgHour - avg120samples),
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
            # Init db
            dbClient = DbLeakDetectionClient()
            dbClient.connectHost("db", "root", "example")
            dbClient.createDatabase("processvalues")
            dbClient.connectDatabase("db", "root", "example", "processvalues")

            dbClient.createTable(
                "SignalAnalogHmiPv",
                "(id INT AUTO_INCREMENT PRIMARY KEY, _tagId VARCHAR(124), metric VARCHAR(3), timestamp DATETIME(6), Output_Pv FLOAT)",
                "processvalues",
            )
            dbClient.createTable(
                "LeakDetectionHourlyAverage",
                "(id INT AUTO_INCREMENT PRIMARY KEY, _tagId VARCHAR(124), metric VARCHAR(3), timestamp DATETIME(6), value FLOAT)",
                "processvalues",
            )
            dbClient.createTable(
                "LeakDetection120SamplesHourlyAverage",
                "(id INT AUTO_INCREMENT PRIMARY KEY, _tagId VARCHAR(124), metric VARCHAR(3), timestamp DATETIME(6), value FLOAT)",
                "processvalues",
            )
            dbClient.createTable(
                "LeakDetectionDeviationHourAnd120SamplesHourlyAverage",
                "(id INT AUTO_INCREMENT PRIMARY KEY, _tagId VARCHAR(124), metric VARCHAR(3), timestamp DATETIME(6), value FLOAT)",
                "processvalues",
            )
            # Init and start Scheduled task "mainloop"
            s = SimpleTaskScheduler(calculateHourlyAverageValues, oneHour_s, 0, 0.1)
            s.start()
            s.join()
        except:
            logging.exception("Leak detection exception, restarting in 10 seconds")
        time.sleep(10)
