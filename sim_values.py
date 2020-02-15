from plclib.mqtt_client import MQTTClient
from threading import Thread
from random import randint
import matplotlib.pyplot as plt
import time

# https://klimaservicesenter.no/faces/desktop/article.xhtml?uri=klimaservicesenteret/Klimanormaler

mqtt = MQTTClient("broker.hivemq.com", 1883, 60, ["wago/ba/sim/out"])

mqttThread = Thread(target=mqtt.loopForever, args=())
mqttThread.start()
time.sleep(2)


class WeatherForcast:
    def __init__(
        self, tag="no tag",
    ):
        self.weather = 0
        self.rain = 0
        self.level = 50
        self.valve = 0
        self.counter = 0
        self.r = 11
        self.checklist = [0, 0, 0, 0, 0, 0]
        self.sumrain = 0

    def randomWeather(self,):
        weatherTypes = (
            ["sun"] * 3
            + ["partlycloudy"] * 3
            + ["cloudy"] * 5
            + ["drizzle"] * 5
            + ["rainy"] * 5
            + ["storm"] * 3
        )
        self.r = self.r + randint(-3, 3)  # Logic for at været ikke kan endres plutselig
        if self.r >= len(weatherTypes):
            self.r = len(weatherTypes) - 1
        elif self.r < 0:
            self.r = 0
        self.weather = weatherTypes[self.r]
        print(self.r)
        print(self.weather)

    def rainWeather(self):
        print(self.weather)
        if self.weather == "drizzle":
            self.rain = randint(1, 2)  # mm regn
        elif self.weather == "rainy":
            self.rain = randint(3, 4)  # mm regn
        elif self.weather == "storm":
            self.rain = randint(5, 6)  # mm regn
        else:
            self.rain = 0
        self.sumrain = self.sumrain + self.rain
        print(self.sumrain)

    def waterLevel(self):
        if self.valve == 1:
            self.level = self.level - 5
        if self.rain == 0:
            self.level = self.level - 2
        else:
            self.level = self.level + self.rain
        print(self.level)

    def openValve(self):
        if self.level > 80:
            self.valve = 1
            print("Valve open")
        else:
            self.valve = 0
            print("Valve closed")

    def check(self):  # For og sjekke gjennomsnittlig vær over tid

        if self.weather == "sun":
            self.checklist[0] = self.checklist[0] + 1
        elif self.weather == "partlycloudy":
            self.checklist[1] = self.checklist[1] + 1
        elif self.weather == "cloudy":
            self.checklist[2] = self.checklist[2] + 1
        elif self.weather == "drizzle":
            self.checklist[3] = self.checklist[3] + 1
        elif self.weather == "rainy":
            self.checklist[4] = self.checklist[4] + 1
        elif self.weather == "storm":
            self.checklist[5] = self.checklist[5] + 1
        print(self.checklist)


weatherForcast = WeatherForcast()
# while True:
for x in range(0, 876):  # På yr er ny varsling vær time. Mulig vi må ha det kontunuerlig
    # mqtt.publish("wago/ba/sim/waterlevel", "6")
    weatherForcast.randomWeather()
    weatherForcast.check()
    weatherForcast.rainWeather()
    # weatherForcast.openValve()
    # weatherForcast.waterLevel()
    time.sleep(0.1)

