from yr.libyr import Yr
import json
import datetime

"""
Using json file from yr.no to find forecast for 8 days.

https://github.com/wckd/python-yr
"""
periode_list = []
from_list = []
to_list = []
symbol_list = []
temp_list = []
rain_list = []
weekday_list = []

today = datetime.datetime.today().weekday()  # Today weekday. Sunday=0 ... Saturday=6

flag = 0
dag = 1

weather = Yr(location_name="Norge/Trøndelag/Trondheim/Trondheim/")

for forecast in weather.forecast(as_json=True):
    forecast = json.loads(forecast)

    # Find the usefull information from json
    periode = int(forecast["@period"])
    from_time = forecast["@from"]
    to_time = forecast["@to"]
    symbol = forecast["symbol"]["@name"]
    temp = forecast["temperature"]["@value"]
    rain = forecast["precipitation"]["@value"]

    if periode == 0 and flag == 0:  # Find the first new period to set as new day.
        flag = 1

    if flag == 1 and periode == 2:  # Using only period 2 for each day. 12:00-18:00
        from_list.append(from_time)
        to_list.append(to_time)
        symbol_list.append(symbol)
        temp_list.append(temp)
        rain_list.append(rain)

        # Since we only have today().weekday() we have to find the following weekdays
        weekday_counter = today + dag
        dag += 1

        if weekday_counter == 6:  # Reset weekday_counter on saturday (6)
            dag = 0
            today = 0

        weekday_list.append(weekday_counter)


print(periode_list)
print(from_list)
print(to_list)
print(symbol_list)
print(temp_list)
print(rain_list)
print(weekday_list)
# print(days_list)

