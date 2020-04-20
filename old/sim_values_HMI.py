from SimulationProgram.mqtt_client import MQTTClient
from threading import Thread
from yr.libyr import Yr
import json
import time
import datetime


"""
Using json file from yr.no to find forecast for 8 days.

https://github.com/wckd/python-yr
"""

# http://www.hivemq.com/demos/websocket-client/
mqtt = MQTTClient("broker.hivemq.com", 1883, 60, ["wago/ba/sim/#"])
mqttThread = Thread(target=mqtt.loopForever, args=())
mqttThread.start()
time.sleep(2)


class SimValuesHMI:
    def __init__(self,):
        self.periode_list = []
        self.from_list = []
        self.to_list = []
        self.symbol_list = []
        self.symbol_number_list = []
        self.temp_list = []
        self.rain_list = []
        self.weekday_list = []
        self.date_list = []

        self.symbol_equal_sun = ["Clear sky", "Fair"]  # 0
        self.symbol_equal_partly_cloudy = ["Partly cloudy"]  # 1
        self.symbol_equal_cloudy = ["Fog", "Cloudy"]  # 2
        self.symbol_equal_rain = [
            "Light rain",
            "Light rain showers",  # NEW
            "Light sleet",
            "Light sleet showers",
            "Light rain showers and thunder",
            "Light sleet showers and thunder",
            "Light rain and thunder",
            "Light sleet and thunder",
            "Rain",
            "Rain showers",
            "Sleet",
            "Sleet showers",
            "Rain showers and thunder",
            "Sleet showers and thunder",
            "Rain and thunder",
            "Sleet and thunder",
        ]  # 3
        self.symbol_equal_storm = [
            "Heavy rain showers",
            "Heavy rain",
            "Heavy sleet",
            "Heavy sleet showers",
            "Heavy rain showers and thunder",
            "Heavy sleet showers and thunder",
            "Heavy rain and thunder",
            "Heavy sleet and thunder",
        ]  # 4
        self.symbol_equal_snow = [
            "Light snow",
            "Snow",
            "Heavy snow",
            "Light snow showers",
            "Snow showers",
            "Heavy snow showers",
            "Light snow showers and thunder",
            "Snow showers and thunder",
            "Heavy snow showers and thunder",
            "Light snow and thunder",
            "Snow and thunder",
            "Heavy snow and thunder",
        ]  # 5

        self.weather_symbol_list = [
            self.symbol_equal_sun,  # 0
            self.symbol_equal_partly_cloudy,  # 1
            self.symbol_equal_cloudy,  # 2
            self.symbol_equal_rain,  # 3
            self.symbol_equal_storm,  # 4
            self.symbol_equal_snow,  # 5
        ]
        self.flag = False
        self.update_weather_forcast = True
        self.json_yr_weather = Yr(location_name="Norge/Trøndelag/Trondheim/Trondheim/")

    def mqttReciveHMI(self,):
        pass

    def updateWeatherForcast(self,):
        if self.update_weather_forcast == True:
            sim.importJsonLongForcast()
            sim.printPrint()
            self.update_weather_forcast = False

    def importJsonLongForcast(self,):

        for forecast in self.json_yr_weather.forecast(as_json=True):
            print(forecast)
            forecast = json.loads(forecast)

            # Find the usefull information from json
            self.periode = int(forecast["@period"])
            self.from_time = forecast["@from"]
            self.to_time = forecast["@to"]
            self.symbol = forecast["symbol"]["@name"]
            self.temp = forecast["temperature"]["@value"]
            self.rain = forecast["precipitation"]["@value"]
            sim.jsonDateToWeekday()
            sim.symbolStringToInt()
            sim.jsonToList()

    def jsonDateToWeekday(self,):
        self.dateStr = self.from_time.split("T")[0]  # Split date from "dateTtime"
        year, month, day = (int(x) for x in self.dateStr.split("-"))  # Convert date to right format
        self.weekday = datetime.date(year, month, day).weekday()  # Find weekday

    def symbolStringToInt(self,):
        self.symbol_number = None
        for idx, self.weather in enumerate(self.weather_symbol_list):
            if self.symbol in self.weather:
                self.symbol_number = idx
            if self.symbol_number == None:
                self.symbol_number = "Not found"

    def jsonToList(self,):
        if self.periode == 0 and self.flag == False:  # Find the first new period to set as new day.
            self.flag = True

        if (
            self.flag == True and self.periode == 2
        ):  # Using only period 2 for each day. 12:00-18:00.
            self.from_list.append(self.from_time)
            self.to_list.append(self.to_time)
            self.symbol_list.append(self.symbol)
            self.symbol_number_list.append(self.symbol_number)
            self.temp_list.append(self.temp)
            self.rain_list.append(self.rain)
            self.weekday_list.append(self.weekday)
            self.date_list.append(self.dateStr)

    def mqttSendHMI(self,):

        MQTT_send = {
            "day1": {
                "weekday": self.weekday_list[0],
                "symbol": self.symbol_number_list[0],
                "temp": self.temp_list[0],
                "rain": self.rain_list[0],
            },
            "day2": {
                "weekday": self.weekday_list[1],
                "symbol": self.symbol_number_list[1],
                "temp": self.temp_list[1],
                "rain": self.rain_list[1],
            },
            "day3": {
                "weekday": self.weekday_list[2],
                "symbol": self.symbol_number_list[2],
                "temp": self.temp_list[2],
                "rain": self.rain_list[2],
            },
        }
        mqtt.publish("wago/ba/sim/out/weatherForcast", MQTT_send.__str__())
        print(MQTT_send)

    def printPrint(self,):
        print("From: " + str(self.from_list))
        print("To: " + str(self.to_list))
        print("Date: " + str(self.date_list))
        print("Weekday: " + str(self.weekday_list))
        print("Symbol: " + str(self.symbol_list))
        print("Symbol number: " + str(self.symbol_number_list))
        print("Temp: " + str(self.temp_list))
        print("Rain: " + str(self.rain_list))


sim = SimValuesHMI()
sim.updateWeatherForcast()
