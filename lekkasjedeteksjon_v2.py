import time
import random
from random import randint

# import numpy
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
        self.today_date = datetime.now().date()
        self.first_run = True
        self.avarage_sum_hour = 0
        self.total_samples_hour = 0
        self.hours_between_average_value = 1
        self.snitt_time = timedelta(hours=self.hours_between_average_value)

        self.list_5_last_days = [[], [], [], [], []]
        self.snittlist_5_last_days = []
        self.five_days_counter = 0
        self.last_day = 0
        self.start_make_snittlist = 2
        self.next_day = 0
        self.sample_counter = 0

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

        self.flowValueTableName = "flowAvarageValues"
        self.flowValueTableFormat = "(id INT AUTO_INCREMENT PRIMARY KEY, metric VARCHAR(3), timestamp DATETIME, avarageFlowValue FLOAT)"
        self.flowValueTableInsert = (
            "INSERT INTO "
            + self.flowValueTableName
            + " (metric, timestamp,  avarageFlowValue) VALUES (%s, %s,  %s)"
        )

        try:  # Create table if not exist
            self.cursor.execute(
                "SELECT * FROM information_schema.tables WHERE table_name='"
                + self.flowValueTableName
                + "'"
            )
            all = self.cursor.fetchall()
            self.db = mysql.connector.connect(
                host="db", user="root", passwd="example", database=self.dbName
            )
            self.cursor = self.db.cursor()
            if len(all) == 0:
                self.cursor.execute(
                    "CREATE TABLE " + self.flowValueTableName + " " + self.flowValueTableFormat
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

    def getLastDateInDB(self,):
        self.cursor = self.db.cursor()
        self.cursor.execute("SELECT * FROM flowValueValues ORDER BY ID DESC LIMIT 1")
        dag = self.cursor.fetchone()
        print(dag)
        print(dag[2].date())  # Siste dag som er registrert i DB
        print(self.today_date)

    def reciveFtValuesDB(self,):
        date1 = self.today_date + timedelta(days=self.next_day)
        date2 = date1 + timedelta(days=1)
        print("Mellom " + str(date1) + " og " + str(date2))

        self.cursor = self.db.cursor()
        self.cursor.execute(
            "SELECT * FROM flowValueValues WHERE timestamp >= %s AND timestamp <=%s", (date1, date2)
        )

        self.day_ft_values = self.cursor.fetchall()
        for self.ft_value in self.day_ft_values:
            pls3.findAverageHourValues()
            # time.sleep(0.2)
        self.next_day = self.next_day + 1
        self.five_days_counter = self.five_days_counter + 1

    def findAverageHourValues(self,):
        self.timestamp = self.ft_value[2]
        self.ft_value_p = self.ft_value[5]

        if self.first_run == True:
            self.start_time = self.ft_value[2]  # .time()
            self.end_time = self.start_time + self.snitt_time
            self.first_run = False
            print("First run")

        if self.timestamp >= self.end_time:
            print("Avaerage: " + str(self.average_ftvalue_hour))
            print("Samples " + str(self.total_samples_hour))
            pls3.appendToList()

            self.val = ("na", self.start_time, self.average_ftvalue_hour)
            self.cursor.execute(self.flowValueTableInsert, self.val)
            self.db.commit()

            self.start_time = self.start_time + self.snitt_time
            self.end_time = self.start_time + self.snitt_time

            self.avarage_sum_hour = 0
            self.total_samples_hour = 0

        if self.start_time <= self.timestamp <= self.end_time:
            self.avarage_sum_hour = self.avarage_sum_hour + self.ft_value_p
            print("")
            # print("Ft value: " + str(self.ft_value_p))
            # print("Sum Hour: " + str(self.avarage_sum_hour))
            # print("Timestamp: " + str(self.timestamp))
            # print("Starttime: " + str(self.start_time))
            # print("Endtime: " + str(self.end_time))

            self.total_samples_hour = self.total_samples_hour + 1
            self.average_ftvalue_hour = self.avarage_sum_hour / self.total_samples_hour

    def appendToList(self,):
        if self.five_days_counter == 5:
            self.five_days_counter = 0
        self.list_5_last_days[self.five_days_counter].append(round(self.average_ftvalue_hour, 2))
        print(self.list_5_last_days)
        # pls3.makeSnittList()

    def makeSnittList(self,):
        if self.five_days_counter != self.last_day:
            self.sample_counter = 0
        if self.five_days_counter == 0:
            self.snittlist_5_last_days.append(round(self.average_ftvalue_hour, 2))
        else:
            self.snittlist_5_last_days[self.sample_counter] = (
                round(
                    self.snittlist_5_last_days[self.sample_counter] + self.average_ftvalue_hour, 2,
                )
                / 2
            )
        print(self.snittlist_5_last_days)
        self.sample_counter = self.sample_counter + 1
        self.last_day = self.five_days_counter

    def plsProgram(self,):
        while self.flag == True:
            # pls3.getLastDateInDB()
            pls3.reciveFtValuesDB()
            # time.sleep(1)


pls3 = PLS3()

while True:
    pls3.plsProgram()
