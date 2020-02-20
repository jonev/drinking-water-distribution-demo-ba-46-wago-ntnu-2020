from plclib.mqtt_client import MQTTClient
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

periode_list = []
from_list = []
to_list = []
symbol_list = []
temp_list = []
rain_list = []
weekday_list = []
date_list = []

flag = False

weather = Yr(location_name="Norge/Trøndelag/Trondheim/Trondheim/")
while True:
    for forecast in weather.forecast(as_json=True):
        print(forecast)
        forecast = json.loads(forecast)

        # Find the usefull information from json
        periode = int(forecast["@period"])
        from_time = forecast["@from"]
        to_time = forecast["@to"]
        symbol = forecast["symbol"]["@name"]
        temp = forecast["temperature"]["@value"]
        rain = forecast["precipitation"]["@value"]

        if periode == 0 and flag == False:  # Find the first new period to set as new day.
            flag = True

        if flag == True and periode == 2:  # Using only period 2 for each day. 12:00-18:00.
            from_list.append(from_time)
            to_list.append(to_time)
            symbol_list.append(symbol)
            temp_list.append(temp)
            rain_list.append(rain)

            dateStr = from_time.split("T")[0]  # Split date from "dateTtime"
            year, month, day = (int(x) for x in dateStr.split("-"))  # Convert date to right format
            weekday = datetime.date(year, month, day).weekday()  # Find weekday
            weekday_list.append(weekday)
            date_list.append(dateStr)

    MQTT_send = {
        "day1": {
            "weekday": weekday_list[0],
            "symbol": symbol_list[0],
            "temp": temp_list[0],
            "rain": rain_list[0],
        },
        "day2": {
            "weekday": weekday_list[1],
            "symbol": symbol_list[1],
            "temp": temp_list[1],
            "rain": rain_list[1],
        },
        "day3": {
            "weekday": weekday_list[2],
            "symbol": symbol_list[2],
            "temp": temp_list[2],
            "rain": rain_list[2],
        },
    }
    mqtt.publish("wago/ba/sim/out/weatherForcast", MQTT_send.__str__())
    # print(from_list)
    # print(to_list)
    # print(symbol_list)
    # print(temp_list)
    # print(rain_list)
    # print(weekday_list)
    # print(date_list)
    # print(MQTT_send)
    time.sleep(3)
