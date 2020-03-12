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
        self.total_deviations_one_day = 0
        self.max_allowed_deviations = 0
        self.days_from_start = 0
        self.sample_nr = 0
        self.deviation_treshold = 0.02

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

        # Create table if not exist ___ flowAvarageValue ___
        self.flowAvarageValueTableName = "flowAvarageValues"
        self.flowAvarageValueTableFormat = "(id INT AUTO_INCREMENT PRIMARY KEY, metric VARCHAR(3), timestamp DATETIME,time TIME, avarageFlowValue FLOAT)"
        self.flowAvarageValueTableInsert = (
            "INSERT INTO "
            + self.flowAvarageValueTableName
            + " (metric, timestamp,time,  avarageFlowValue) VALUES (%s, %s, %s, %s)"
        )

        self.cursor.execute(
            "DROP TABLE IF EXISTS " + self.flowAvarageValueTableName
        )  # Resetter tabellen ved første oppstart om den finnes
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

        # Create table if not exist __ flowAvarageDaysValue___

        self.flowAvarageDaysValueTableName = "flowAvarageValuesDays"
        self.flowAvarageDaysValueTableFormat = "(time TIME PRIMARY KEY, avarageFlowValueDays FLOAT)"
        self.flowAvarageDaysValueTableInsert = (
            "INSERT INTO "
            + self.flowAvarageDaysValueTableName
            + " (time, avarageFlowValueDays) VALUES (%s, %s)"
        )

        self.cursor.execute(
            "DROP TABLE IF EXISTS " + self.flowAvarageDaysValueTableName
        )  # Resetter tabellen ved første oppstart om den finnes
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

    def getDayCounterFromSim(self,):
        self.day_counter = self.receivedObject["dayCounter"]
        print(self.day_counter)

    def getLastDateInDB(self,):
        self.cursor = self.db.cursor()
        self.cursor.execute("SELECT * FROM flowValueValues ORDER BY ID DESC LIMIT 1")
        dag = self.cursor.fetchone()
        self.last_day_in_DB = dag[2].date()
        print(dag)
        print()  # Siste dag som er registrert i DB
        print(self.todays_date)
        print("")

    def reciveFtValuesDB(self,):
        pls3.getLastDateInDB()
        date1 = self.todays_date + timedelta(days=self.days_from_start)
        date2 = date1 + timedelta(days=1)
        self.cursor = self.db.cursor()
        self.cursor.execute(
            "SELECT * FROM flowValueValues WHERE timestamp >= %s AND timestamp <=%s",
            (date1, date2),
        )

        self.day_ft_values = self.cursor.fetchall()
        for self.ft_value in self.day_ft_values:
            pls3.findAverageXMinValues()
        self.days_from_start = self.days_from_start + 1

    def findAverageXMinValues(self,):
        self.timestamp = self.ft_value[2]
        self.ft_value_p = self.ft_value[5]

        if self.first_run == True:
            self.start_time = self.ft_value[2]
            self.end_time = self.start_time + self.hours_between_average_value_dt
            self.first_run = False
            print("First run")

        if self.timestamp >= self.end_time:
            print("Avaerage: " + str(self.average_ftvalue_hour))
            print("Samples " + str(self.samples_in_sum_xmin))

            self.val = (
                "na",
                self.start_time,
                self.start_time.time(),
                self.average_ftvalue_hour,
            )
            self.cursor.execute(self.flowAvarageValueTableInsert, self.val)
            self.db.commit()
            pls3.sqlMakeSnittList()

            self.start_time = self.start_time + self.hours_between_average_value_dt
            self.end_time = self.start_time + self.hours_between_average_value_dt

            self.sum_xmin = 0
            self.samples_in_sum_xmin = 0

        if self.start_time <= self.timestamp <= self.end_time:
            self.sum_xmin = self.sum_xmin + self.ft_value_p

            self.samples_in_sum_xmin = self.samples_in_sum_xmin + 1
            self.average_ftvalue_hour = self.sum_xmin / self.samples_in_sum_xmin

    def sqlMakeSnittList(self,):
        date1 = self.start_time.date() + timedelta(days=1)
        date2 = date1 - timedelta(days=5)
        time_timestamp = self.start_time.time()

        self.cursor = self.db.cursor()
        self.cursor.execute(
            "SELECT * FROM flowAvarageValues WHERE timestamp < %s AND timestamp >=%s AND time=%s ",
            (date1, date2, time_timestamp),
        )
        myresult = self.cursor.fetchall()
        self.sum_snittvalue_days = 0

        for self.sample in myresult:
            self.timestamp_time_min = self.sample[3]
            self.average_ftvalue = self.sample[4]
            self.sum_snittvalue_days = self.sum_snittvalue_days + self.average_ftvalue
            print(self.sample)

        self.snittvalue_days = self.sum_snittvalue_days / len(myresult)
        pls3.findLeak()
        self.val = (self.timestamp_time_min, self.snittvalue_days, self.snittvalue_days)

        self.cursor.execute(
            self.flowAvarageDaysValueTableInsert
            + " ON DUPLICATE KEY UPDATE avarageFlowValueDays=%s",
            self.val,
        )  # Insert avargeDays values
        self.db.commit()

    def findLeak(self,):
        if self.days_from_start == 0:
            self.average_values_over_days.append(round(self.snittvalue_days, 2))
            self.deviation_list.append(0)
        else:
            self.deviation_list[self.sample_nr] = abs(
                round(self.average_ftvalue - self.average_values_over_days[self.sample_nr], 2)
            )
            self.average_values_over_days[self.sample_nr] = round(self.snittvalue_days, 2)

            print("Avviksliste: " + str(self.deviation_list))
            if self.deviation_list[self.sample_nr] > self.deviation_treshold:
                self.total_deviations_one_day = self.total_deviations_one_day + 1
            self.sample_nr = self.sample_nr + 1

        if self.total_deviations_one_day > self.max_allowed_deviations:
            print("Lekkasje")

        if self.sample_nr == len(self.average_values_over_days):
            self.sample_nr = 0
            self.total_deviations_one_day = 0
        print("Snittliste dager: " + str(self.average_values_over_days))
        print("Dag fra start: " + str(self.days_from_start))
        print("Antall avvik: " + str(self.total_deviations_one_day))

        print("")

    def plsProgram(self,):
        while self.flag == True:
            pls3.reciveFtValuesDB()
            # time.sleep(1)


pls3 = PLS3()

while True:
    pls3.plsProgram()
