import time
import random
from random import randint
import paho.mqtt.client as mqtt
from threading import Thread
import json
import mysql.connector
from datetime import timedelta, datetime


class PLS3:
    def __init__(self,):
        self.dbName = "processvalues"
        self.db = mysql.connector.connect(
            host="db", user="root", passwd="example", database=self.dbName
        )
        self.cursor = self.db.cursor()

        self.flag = True
        self.first_run = True
        self.todays_date = datetime.now().date()

        self.sum_xmin = 0
        self.samples_in_sum_xmin = 0

        self.hours_between_average_value_float = 0.5
        self.hours_between_average_value_dt = timedelta(
            hours=self.hours_between_average_value_float
        )

        self.average_values_over_days = []
        self.deviation_list = []

        self.max_allowed_deviations = int(
            (24 / self.hours_between_average_value_float) * 0.75
        )  # 75% av totale samples
        self.deviation_treshold = 1.5
        self.total_deviations_one_day = 0

        self.days_from_start = 0
        self.sample_nr = 0

        self.time_waiting = 0
        self.average_ftvalue_xmin = 0

        # MQTT Setup

        mqttBroker = "broker.hivemq.com"
        mqttPort = 1883
        self.mqttTopicSubscribe = "wago/ba/sim/out/PLS2"
        self.mqttTopicPublish = "wago/ba/sim/out/PLS2"
        self.mqttClient = mqtt.Client()
        self.mqttClient.connect(mqttBroker, mqttPort, 60)
        self.mqttClient.on_connect = self.on_connect
        self.mqttClient.on_message = self.on_message
        self.mqttThread = Thread(target=self.mqttClient.loop_forever, args=())
        self.mqttThread.start()
        time.sleep(2)

        self.mqttClient.publish(self.mqttTopicPublish, payload="MQTT Leakdetection is running...")

        # Create table if not exist ___flowAvarageValue___
        self.flowAvarageValueTableName = "flowAvarageValues"
        self.flowAvarageValueTableFormat = "(id INT AUTO_INCREMENT PRIMARY KEY, metric VARCHAR(3), timestamp DATETIME, from_start TIME, to_end TIME, avarageFlowValue FLOAT)"
        self.flowAvarageValueTableInsert = (
            "INSERT INTO "
            + self.flowAvarageValueTableName
            + " (metric, timestamp, from_start, to_end, avarageFlowValue) VALUES (%s, %s, %s, %s, %s)"
        )

        self.cursor.execute(
            "DROP TABLE IF EXISTS " + self.flowAvarageValueTableName
        )  # Delete table if it's already excist. #Kan muligens fjernes når det er funksjonelt
        try:
            self.cursor.execute(
                "SELECT * FROM information_schema.tables WHERE table_name='"
                + self.flowAvarageValueTableName
                + "'"
            )
            all = self.cursor.fetchall()
            self.db = mysql.connector.connect(
                host="db", user="root", passwd="example", database=self.dbName
            )
            self.cursor = self.db.cursor()
            if len(all) == 0:
                self.cursor.execute(
                    "CREATE TABLE "
                    + self.flowAvarageValueTableName
                    + " "
                    + self.flowAvarageValueTableFormat
                )
        except Exception as ex:
            print(ex)

        # Create table if not exist __flowAvarageDaysValue___

        self.flowAvarageDaysValueTableName = "flowAvarageValuesDays"
        self.flowAvarageDaysValueTableFormat = "(from_start TIME PRIMARY KEY, to_end TIME, avarageFlowValueDays FLOAT, deviation FLOAT)"
        self.flowAvarageDaysValueTableInsert = (
            "INSERT INTO "
            + self.flowAvarageDaysValueTableName
            + " (from_start, to_end, avarageFlowValueDays, deviation) VALUES (%s, %s, %s, %s)"
        )

        self.cursor.execute(
            "DROP TABLE IF EXISTS " + self.flowAvarageDaysValueTableName
        )  # Delete table if it's already excist. #Kan muligens fjernes når det er funksjonelt
        try:
            self.cursor.execute(
                "SELECT * FROM information_schema.tables WHERE table_name='"
                + self.flowAvarageDaysValueTableName
                + "'"
            )
            all = self.cursor.fetchall()
            self.db = mysql.connector.connect(
                host="db", user="root", passwd="example", database=self.dbName
            )
            self.cursor = self.db.cursor()
            if len(all) == 0:
                self.cursor.execute(
                    "CREATE TABLE "
                    + self.flowAvarageDaysValueTableName
                    + " "
                    + self.flowAvarageDaysValueTableFormat
                )
        except Exception as ex:
            print(ex)

    def on_connect(self, client, userdata, flags, rc):
        print("MQTT Connected with result code " + str(rc))
        self.mqttClient.subscribe(self.mqttTopicSubscribe)

    def on_message(self, client, userdata, msg):
        # print(msg.topic + str(msg.payload))
        # TODO not thread safe
        self.receivedObject = json.loads(str(msg.payload, encoding="utf-8"))

    # Utgår
    def getDayCounterFromSim(self,):
        self.day_counter = self.receivedObject["dayCounter"]
        print(self.day_counter)

    # Utgår
    def getLastDateInDB(self,):
        """
        Get the last date added to the database. In format YYYY-MM-DD.
        """
        self.cursor = self.db.cursor()
        self.cursor.execute("SELECT * FROM flowValueValues ORDER BY ID DESC LIMIT 1")
        dag = self.cursor.fetchone()
        self.db.commit()
        self.last_day_in_DB = dag[2].date()

    # Utgår
    def checkIfNewDay(self,):
        """
        Checks if the database has a full day of samples available to be imported.
        """

        pls3.getLastDateInDB()
        if self.first_run == True and self.last_day_in_DB > self.todays_date:  # Only on first run
            self.todays_date = self.last_day_in_DB - timedelta(
                days=1
            )  # If todays date is less than last day in database, import todays samples.
            pls3.reciveFtValuesDB()  # Recive day samples from database

        elif self.last_day_in_DB > self.todays_date:

            pls3.reciveFtValuesDB()  # Recive day samples from database
            self.time_waiting = 0  # Reset waiting time
        else:
            print(
                "Waiting on current database day to be finished"
            )  # Printing waiting on a full day with samples
            print("Current DB day: " + str(self.last_day_in_DB))
            print("Last day run: " + str(self.todays_date - timedelta(days=1)))
            self.time_waiting = self.time_waiting + 1
            print(self.time_waiting)
            time.sleep(2)

    def reciveFtValuesDB(self,):

        """
        Get values from database. Import values from date1 to date2
        """
        date1 = self.todays_date
        date2 = date1 + timedelta(days=1)
        self.cursor = self.db.cursor()
        self.cursor.execute(
            "SELECT * FROM flowValueValues WHERE timestamp >= %s AND timestamp <=%s",
            (date1, date2),
        )

        self.day_ft_values = self.cursor.fetchall()
        for self.ft_value in self.day_ft_values:  # Go through all samples from date1 to date2
            pls3.findAverageXMinValues()

        # After one day is importet and checked for leak. These two varibles make it possible to check for new day.
        self.days_from_start = self.days_from_start + 1  # Days from start in INT
        self.todays_date = self.todays_date + timedelta(
            days=1
        )  # The new date to import samples for. (Next day)

    def findAverageXMinValues(self,):
        """
        Find average values for x number of minutes.
        x number of minutes is set in self.hours_between_average_value_float in hours.
        Example self.hours_between_average_value_float=0.5 is the same as 30 minutes.
        """

        self.timestamp = self.ft_value[2]  # Import timestamp from samples
        self.ft_value_p = self.ft_value[5]  # Import flow value from samples

        if self.first_run == True:  # For first run
            self.start_time = self.ft_value[
                2
            ]  # Set start time the first timestamp imported from database
            self.end_time = self.start_time + self.hours_between_average_value_dt
            self.first_run = False
            print("First run")

        if self.timestamp >= (
            self.end_time
        ):  # If the program has gone through the samples ​​it should find average value for the given time period.
            print("Avaerage: " + str(self.average_ftvalue_xmin))
            print("Samples " + str(self.samples_in_sum_xmin))

            self.val = (
                "na",
                self.start_time,
                self.start_time.time(),
                self.end_time,
                self.average_ftvalue_xmin,
            )
            self.cursor.execute(
                self.flowAvarageValueTableInsert, self.val
            )  # Send avarage value to new table flowAvarageValues
            self.db.commit()
            pls3.sqlMakeSnittList()  # Compares average values ​​between each day that have the same time span

            self.start_time = (
                self.start_time + self.hours_between_average_value_dt
            )  # Find new start time for the new average value
            self.end_time = (
                self.start_time + self.hours_between_average_value_dt
            )  # Find new end time for the new average value

            self.sum_xmin = 0  # Reset variables used to find the average value
            self.samples_in_sum_xmin = 0

        if (
            self.start_time <= self.timestamp <= self.end_time
        ):  # If the sample timestamp is between start and end time, use this sample to find average value for given time period.
            self.sum_xmin = self.sum_xmin + self.ft_value_p

            self.samples_in_sum_xmin = self.samples_in_sum_xmin + 1
            self.average_ftvalue_xmin = (
                self.sum_xmin / self.samples_in_sum_xmin
            )  # Find the average value

    def sqlMakeSnittList(self,):
        """
        Compares average values ​​between each day that have the same time span
        """
        date1 = self.start_time.date() + timedelta(
            days=1
        )  # Since start_time.date is the day we are working on we want to import everyting > start_time.date+1day
        date2 = date1 - timedelta(days=5)  # Import values ​​from five days back if they exists
        time_timestamp = (
            self.start_time.time()
        )  # Since we are comparing average values with the same time span we have to import the average values with the same time span

        self.cursor = self.db.cursor()
        self.cursor.execute(
            "SELECT * FROM flowAvarageValues WHERE timestamp < %s AND timestamp >=%s AND from_start=%s ",
            (date1, date2, time_timestamp),
        )  # Import average values with the same time span and between date1 and date2
        myresult = self.cursor.fetchall()
        self.sum_avarage_value_days = 0  # Reset sum of avarage value days

        for self.sample in myresult:
            self.timestamp_from = self.sample[3]
            self.timestamp_to = self.sample[4]
            self.average_ftvalue = self.sample[5]
            self.sum_avarage_value_days = (
                self.sum_avarage_value_days + self.average_ftvalue
            )  # Summing all avarage values with same time span
            print(self.sample)

        self.average_value_days = self.sum_avarage_value_days / len(
            myresult
        )  # Find the avarage values on the samples in each day that have same timespan
        pls3.findLeak()
        self.val = (
            self.timestamp_from,
            self.timestamp_to,
            self.average_value_days,
            self.current_deviation,
            self.average_value_days,
            self.current_deviation,
        )

        self.cursor.execute(
            self.flowAvarageDaysValueTableInsert
            + " ON DUPLICATE KEY UPDATE avarageFlowValueDays=%s,deviation=%s",
            self.val,
        )  # Insert avarage values for days in new table. If a value for given time already exist, then update avarageFlowValueDays and deviation.
        self.db.commit()

    def findLeak(self,):
        """
        Use average values for days with same timespan and compare them.
        The total deviation counter (self.total_deviations_one_day) is counting how many samples where the deviation is over the given treshold.
        If the total deviation counter is above max allowed deviations (self.max_allowed_deviations) the program indicate a leak.
        """
        if self.days_from_start == 0:  # First day
            self.average_values_over_days.append(round(self.average_value_days, 4))
            self.deviation_list.append(0)  # Append zero as deviation and doesnt look for leak.
        else:
            self.deviation_list[self.sample_nr] = abs(
                round(self.average_ftvalue - self.average_values_over_days[self.sample_nr], 3)
            )  # Find the deviation between current avarage flow value for x min and the avarage of avarage flow value for x min in the last day/days in the same timestamp.
            self.average_values_over_days[self.sample_nr] = round(
                self.average_value_days, 4
            )  # Add the avarage value over days in list. #Kan fjernes

            print("Avviksliste: " + str(self.deviation_list))
            if (
                self.deviation_list[self.sample_nr] > self.deviation_treshold
            ):  # Check if the deviation is over the treshold
                self.total_deviations_one_day = (
                    self.total_deviations_one_day + 1
                )  # Count total deviations over treshold

        self.current_deviation = self.deviation_list[self.sample_nr]  # Current deviation.
        self.sample_nr = self.sample_nr + 1
        if (
            self.total_deviations_one_day > self.max_allowed_deviations
        ):  # Check if it is to many deviatons in one day.
            print("Lekkasje")
            self.flag == False

        if self.sample_nr == 48:  # Resett samplenr # Må finne en bedre metodet
            self.sample_nr = 0
            self.total_deviations_one_day = 0
        print("Snittliste dager: " + str(self.average_values_over_days))
        print("Dag fra start: " + str(self.days_from_start))
        print("Antall avvik: " + str(self.total_deviations_one_day))

        print("")

    def plsProgram(self,):
        while self.flag == True:
            pls3.checkIfNewDay()
            # time.sleep(1)


pls3 = PLS3()

while True:
    pls3.plsProgram()
