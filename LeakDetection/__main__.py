from utils.scheduler import SimpleTaskScheduler
from LeakDetection.dbLeakDetectionClient import DbLeakDetectionClient
from LeakDetection.divcalculations import DivCalculations
from LeakDetection.datastore import FtData
import datetime  # Best compatible with mysql
import logging
import time

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

version = "0.0.7"
sampleTime_s = 5  # DO NOT CHANGE - One sample is in real time 2 hours. 12 samples pr hour.
oneDayIsSimulatedTo_s = 60  # DO NOT CHANGE
oneHour_s = oneDayIsSimulatedTo_s / 24
simulatedSamplesPerDay = 96  # DO NOT CHANGE

# Updates the number of points over the limit
## To increase the performance: "If the point is over the limit" is stored in a queue
## This avoids rolling through and checking all hour values. 
## One is added and one is removed, and the number of points is updated.
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

# Calculates values regarding one flow transmitter
def handleFt(dbClient, start, end, ftData):
    # Collects sample values from database
    values = dbClient.getValuesBetweenTimestamps("SignalAnalogHmiPv", start, end, ftData._tagId,)
    avgHour = DivCalculations.avgValue(values, 4)
    dbClient.pushValueOnTimestamp("LeakDetectionHourlyAverage", start, ftData._tagId, avgHour)
    # Collecting the last 120 samples of hourly averages values
    values120SamplesHourlyAverages = dbClient.getAverageHourValues(
        "LeakDetectionHourlyAverage",
        ftData._tagId,
        (start.second - 0.1) % 60,
        (end.second + 0.1) % 60,
        5,
    )
    avg120samples = DivCalculations.avgValue(values120SamplesHourlyAverages, 4)
    dbClient.pushValueOnTimestamp(
        "LeakDetection120SamplesHourlyAverage", start, ftData._tagId, avg120samples
    )

    # Calculating points over limit
    ## Calculating % differance between average hourly and average hourly 120 last samples
    ## (Avoiding dividing on zero)
    if avg120samples != 0.00:
        diffNowInPercent = avgHour / avg120samples
    else:
        diffNowInPercent = 0.0

    # Finding and storing points over 10%, 20% and 30% of the average value
    ftData.pointsOver10 = updatePoints(
        diffNowInPercent, 1.10, ftData.pointsOver10, ftData.queuePointsOver10
    )
    ftData.pointsOver20 = updatePoints(
        diffNowInPercent, 1.20, ftData.pointsOver20, ftData.queuePointsOver20
    )
    ftData.pointsOver30 = updatePoints(
        diffNowInPercent, 1.30, ftData.pointsOver30, ftData.queuePointsOver30
    )
    dbClient.pushPointsOnTimestamp(
        "LeakDetectionAlarmPoints",
        start,
        ftData._tagId,
        ftData.pointsOver10,
        ftData.pointsOver20,
        ftData.pointsOver30,
    )
    return avgHour


# Calculates the difference between in and out flow, and store it in the database
def handleFtBalance(dbClient, start, end, inFlowAvg, outFlowAvg, ftData):
    dbClient.pushValueOnTimestamp(
        "LeakDetectionBalanceHourlyAverage", start, ftData._tagId, (inFlowAvg - outFlowAvg)
    )

# Scheduled task
def calculateHourlyAverageValues(datetimestamp):
    global FT01, FT02, FT03, FT04, FT05, FT06, FT07
    try:
        timetaking = datetime.datetime.now()
        # Adding delay to the time range, be certain that the data is present
        datetimestamp = datetimestamp - datetime.timedelta(seconds=5)
        # Time range: Defines which data is used in this execution
        start = datetimestamp - datetime.timedelta(seconds=oneHour_s)
        end = datetimestamp

        # FT Values
        avgHourFT01 = handleFt(dbClient, start, end, FT01)
        avgHourFT02 = handleFt(dbClient, start, end, FT02)
        avgHourFT03 = handleFt(dbClient, start, end, FT03)
        avgHourFT04 = handleFt(dbClient, start, end, FT04)
        avgHourFT05 = handleFt(dbClient, start, end, FT05)
        avgHourFT06 = handleFt(dbClient, start, end, FT06)
        avgHourFT07 = handleFt(dbClient, start, end, FT07)
        # Flow balance
        handleFtBalance(
            dbClient, start, end, avgHourFT07, (avgHourFT01 + avgHourFT06), FT07_is_FT01_FT06,
        )
        handleFtBalance(
            dbClient, start, end, avgHourFT06, (avgHourFT02 + avgHourFT05), FT06_is_FT02_FT05,
        )
        handleFtBalance(
            dbClient, start, end, avgHourFT05, (avgHourFT03 + avgHourFT04), FT05_is_FT03_FT04,
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
    while True: # Automatically restart logic
        try:
            logging.info("Starting Leakdetection in __main__ version: " + version)
            logging.info("Waiting for db to start - 30 seconds")
            time.sleep(30)

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

            dbClient.createTable(
                "LeakDetectionBalanceHourlyAverage",
                "(id INT AUTO_INCREMENT PRIMARY KEY, _tagId VARCHAR(124), metric VARCHAR(3), timestamp DATETIME(6), value FLOAT)",
            )

            # FT data, for calculations
            FT01 = FtData("WaterFlowFT01_Pv")
            FT02 = FtData("WaterFlowFT02_Pv")
            FT03 = FtData("WaterFlowFT03_Pv")
            FT04 = FtData("WaterFlowFT04_Pv")
            FT05 = FtData("WaterFlowFT05_Pv")
            FT06 = FtData("WaterFlowFT06_Pv")
            FT07 = FtData("WaterFlowFT07_Pv")

            FT07_is_FT01_FT06 = FtData("FT07_is_FT01_FT06")
            FT06_is_FT02_FT05 = FtData("FT06_is_FT02_FT05")
            FT05_is_FT03_FT04 = FtData("FT05_is_FT03_FT04")

            # Init and start Scheduled task "calculateHourlyAverageValues"
            s = SimpleTaskScheduler(calculateHourlyAverageValues, oneHour_s, 0, 0.1)
            s.start()
            s.join()
        except:
            logging.exception("Leak detection exception, restarting in 10 seconds")
        time.sleep(10)
