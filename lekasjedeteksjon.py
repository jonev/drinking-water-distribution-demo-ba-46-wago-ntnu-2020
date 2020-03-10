# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 23:03:33 2020

@author: peder
"""
import time
import random
from random import randint
import matplotlib.pyplot as plt
import numpy
import paho.mqtt.client as mqtt
from threading import Thread
import json
import mysql.connector
from datetime import timedelta, datetime


class PLS3:
    def __init__(self,):

        # Lister
        self.ft_values_day_list = []
        self.timestamp_list = []
        self.list_of_ft_values_day_lists = []
        self.list_of_average_ft_values_lists = []

        # Tellere
        self.sample_nr = 0
        self.day_counter = 0
        self.total_snitt_list_appended = 0
        self.number_of_deviation_01 = 0
        self.number_of_deviation_0x = 0

        # Setpunkt
        self.compare_when_0x = (
            5  # Hvor mange snittlister det må være før ma sammenligner på lang tidshorisont
        )
        self.total_samples_one_day = 10
        self.find_avarage_value_on_every = 5  # På hvilken dag man skal regne ut snittet
        self.deviation_treshold = 2
        self.constant_leak_value = 0
        self.gradual_leak_value_for_every_day = 0

        # Testing
        self.compare_01_command = False
        self.flag = True

        # DB Setup

        # DB SETUP

        # self.dbName = "processvalues"
        self.db = mysql.connector.connect(
            host="db", user="root", passwd="example", database="processvalues"
        )

        self.cursor = self.db.cursor()
        """
        try:  # Add if not exist
            self.cursor.execute("CREATE DATABASE " + self.dbName)
        except Exception as ex:
            print(ex)

        self.flowValueTableName = "flowValueValues"
        self.flowValueTableFormat = "(id INT AUTO_INCREMENT PRIMARY KEY, metric VARCHAR(3), timestamp TIMESTAMP,daycounter INT,samplenr INT, FlowValue FLOAT)"
        self.flowValueTableInsert = (
            "INSERT INTO "
            + self.flowValueTableName
            + " (metric, timestamp,daycounter, samplenr, FlowValue) VALUES (%s, %s, %s,%s, %s)"
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
        """

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
        self.today_date = datetime.now().date() + timedelta(
            days=3
        )  # Grunnet feil dato fra datetime
        self.current_day = self.receivedObject["dayCounter"]

    def on_connect(self, client, userdata, flags, rc):
        print("MQTT Connected with result code " + str(rc))
        self.mqttClient.subscribe(self.mqttTopicSubscribe)

    def on_message(self, client, userdata, msg):
        # print(msg.topic + str(msg.payload))
        # TODO not thread safe
        self.receivedObject = json.loads(str(msg.payload, encoding="utf-8"))

    def reciveValuesFromMQTT(self,):
        MQTT_recived = self.receivedObject
        self.day_counter = MQTT_recived["dayCounter"]
        print(self.day_counter)

    def newDay(self):
        self.new_day = False
        if self.current_day != self.day_counter:
            self.new_day = True
            self.current_day = self.current_day + 1
            print(self.new_day)

    def reciveFtValuesDB(self,):
        date1 = self.day_counter
        date2 = date1 + timedelta(days=5)
        print("Mellom " + str(date1) + " og " + str(date2))
        mycursor = mydb.cursor()
        mycursor.execute(
            "SELECT * FROM flowValueValues WHERE timestamp >= %s AND timestamp <%s", (date1, date2)
        )

        day_ft_values = self.cursor.fetchall()

        for ft_value in day_ft_values:
            print(ft_value[5])

    def simLeak(self):
        if self.new_day == True:
            self.gradual_leak_value_for_every_day = self.gradual_leak_value_for_every_day + 0.2
        if self.day_counter == 17:  # Når lekkasjen skal slå inn
            self.constant_leak_value = 0  # Mengde lekkasje
        self.new_day = False

    def randomFTvalue(self,):
        self.ft_value = round(
            10 * random.uniform(0.9, 1.1)
            + self.constant_leak_value
            + self.gradual_leak_value_for_every_day,
            2,
        )  # Random ft verdi

    def ftValueToDayList(self,):
        if self.new_day == True:

            date1 = self.today_date + (timedelta(days=self.day_counter))
            date2 = date1 + timedelta(days=1)
            print("Mellom " + str(date1) + " og " + str(date2))
            self.cursor = self.db.cursor()
            self.cursor.execute(
                "SELECT * FROM flowValueValues WHERE timestamp >= %s AND timestamp <%s",
                (date1, date2),
            )
            day_ft_values = self.cursor.fetchall()

            for self.ft_value in day_ft_values:
                # print(self.ft_value[5])
                self.ft_values_day_list.append(self.ft_value[5])  # Ft verdi blir lagt til i liste
                # self.timestamp_list.append(self.sample_nr)  # Sample nr blir lagt til i liste
                # self.sample_nr = (
                #    self.sample_nr + 1
                # )  # Øker sample nummer for vær runde kjørt, altså for vær nye ft verdi
                # print(self.ft_values_day_list)
            print("Liste fra dag" + str(date1) + ": " + str(self.ft_values_day_list))
            self.new_day == False

    def newDayNewList(self,):
        if (
            self.sample_nr == self.total_samples_one_day
        ):  # Skjekker om antall samples er lik ønsket antall samples for en dag. I teorien om dagen er ferdig.
            self.day_counter = self.day_counter + 1  # Teller da opp for ny dag
            print("")
            print("Dag: " + str(self.day_counter))
            print("Dagsliste: " + str(self.ft_values_day_list))
            self.list_of_ft_values_day_lists.append(
                self.ft_values_day_list
            )  # Legger ft verdiene for en hel dag i en ny liste som liste.
            self.ft_values_day_list = []  # Resetter dagslisten for nye verdier
            self.timestamp_list = []  # Resetter dagslisten for nye verdier
            self.sample_nr = 0  # Resetter samplenr slik at sample 1 for ny dag blir 1
            self.new_day = True
            time.sleep(1)

    def avarageListForXDay(self,):
        if (
            self.day_counter % self.find_avarage_value_on_every == 0 and self.sample_nr == 0
        ):  # Sjekker om det har gått x dager og om det er første sample for denne dagen
            self.summer_x_days_list = [
                0
            ] * self.total_samples_one_day  # Klargjøre liste for å legge inn summeringsverdi fra x antall dager
            self.average_ft_values_for_x_days_list = [
                0
            ] * self.total_samples_one_day  # Klargjøre liste for å legge inn snittverdi fra x antall dager
            for dag in range(0, self.find_avarage_value_on_every):  # Går igjennom dag 1 til dag x
                for sample in range(
                    0, self.total_samples_one_day
                ):  # Går igjennom alle samples for hver dag
                    self.summer_x_days_list[sample] = round(
                        self.summer_x_days_list[sample]
                        + self.list_of_ft_values_day_lists[dag][sample],
                        2,
                    )  # Summerer alle verdiene i samme liste index fra dag 1 til dag x
            self.list_of_ft_values_day_lists = (
                []
            )  # Resetter listen for ft verdier for x antall dager
            for sample in range(
                0, self.total_samples_one_day
            ):  # Går gjenneom alle summerte verdier i summerlisten
                self.average_ft_values_for_x_days_list[sample] = round(
                    (self.summer_x_days_list[sample] / self.find_avarage_value_on_every), 2
                )  # Finner snittet alle verdiene i samme liste index fra dag 1 til dag x
            print("")
            print(
                "Snitt liste for hver "
                + str(self.find_avarage_value_on_every)
                + " dag: "
                + str(self.average_ft_values_for_x_days_list)
            )
            pls3.snittListeInListOfSnitts()  # Starter ny funksjon

    def snittListeInListOfSnitts(self,):
        self.list_of_average_ft_values_lists = [
            self.average_ft_values_for_x_days_list
        ] + self.list_of_average_ft_values_lists  # Legger snittlisten for dag 0 til x i en liste der alle snittliste samles
        self.total_snitt_list_appended = (
            self.total_snitt_list_appended + 1
        )  # Holder kontroll på hvor mange lister som har blitt lagt til
        if (
            self.total_snitt_list_appended > 1
        ):  # Når to snittlister for dag 0 til x starter compare funksjon
            self.compare_01_command = True
        print("Alle snitt lister:" + str(self.list_of_average_ft_values_lists))

    def compareAvarageList01(self,):
        if self.compare_01_command == True:
            self.deviation_list_01 = [0] * self.total_samples_one_day  # Klargjører liste
            for sample in range(0, self.total_samples_one_day):
                self.deviation_list_01[sample] = round(
                    (
                        self.list_of_average_ft_values_lists[0][sample]
                        - self.list_of_average_ft_values_lists[1][sample]
                    ),
                    2,
                )  # Finner avviket mellom snittliste 0 og 1
            for sample in range(
                0, self.total_samples_one_day
            ):  # Går gjenom alle avviksvariablene i listen
                if (
                    self.deviation_list_01[sample] > self.deviation_treshold
                ):  # Skjekker om avviksvariablene er strørre en deviation_treshold
                    self.number_of_deviation_01 = (
                        self.number_of_deviation_01 + 1
                    )  # Følger med hvor mange avviksvaribaler som er over deviation_treshold
            print("")
            print("Sammenligner snittliste 0 med snittliste 1")
            print("Avvikliste: " + str(self.deviation_list_01))
            if (
                self.number_of_deviation_01 > self.total_samples_one_day * 0.75
            ):  # Hvis for mange avviksvariabler er over deviation_treshold
                print("Mulig Lekkasje")
            else:
                print("Ingen lekkasje")

            self.compare_01_command = False  # Ferdi med sammenligningen
            self.compare_0x_command = True

    def compareAvarageList0x(self,):
        if (
            self.total_snitt_list_appended % self.compare_when_0x == 0
            and not self.total_snitt_list_appended == 0
            and self.compare_0x_command == True
        ):
            print("")
            print("Sammenligner snittliste 0 med snittliste " + str(self.compare_when_0x))
            print(str(self.list_of_average_ft_values_lists[0]))
            print(str(self.list_of_average_ft_values_lists[self.compare_when_0x - 1]))
            print("")
            self.deviation_list_0x = [0] * self.total_samples_one_day  # Klargjører liste
            for sample in range(0, self.total_samples_one_day):
                self.deviation_list_0x[sample] = round(
                    (
                        self.list_of_average_ft_values_lists[0][sample]
                        - self.list_of_average_ft_values_lists[self.compare_when_0x - 1][sample]
                    ),
                    2,
                )  # Finner avviket mellom snittliste 0 og 1
            for sample in range(
                0, self.total_samples_one_day
            ):  # Går gjenom alle avviksvariablene i listen
                if (
                    self.deviation_list_0x[sample] > self.deviation_treshold
                ):  # Skjekker om avviksvariablene er strørre en deviation_treshold
                    self.number_of_deviation_0x = (
                        self.number_of_deviation_0x + 1
                    )  # Følger med hvor mange avviksvaribaler som er over deviation_treshold #### DENNE LISTEN MÅ RESETES FOR Å FJERNE LEKKASJE
            print("Avvikliste: " + str(self.deviation_list_0x))
            if (
                self.number_of_deviation_0x > self.total_samples_one_day * 0.75
            ):  # Hvis for mange avviksvariabler er over deviation_treshold
                print("Mulig gradvis lekkasje")
            else:
                print("Ingen gravis lekkasje")
            self.compare_0x_command = False

    def plsProgram(self,):
        while self.flag == True:
            pls3.reciveValuesFromMQTT()
            pls3.newDay()
            # pls3.reciveFtValuesDB()
            # pls3.simLeak()
            # pls3.randomFTvalue()
            pls3.ftValueToDayList()
            # pls3.newDayNewList()
            # pls3.avarageListForXDay()
            # pls3.compareAvarageList01()
            # pls3.compareAvarageList0x()
            time.sleep(1)


pls3 = PLS3()

while True:
    pls3.plsProgram()

