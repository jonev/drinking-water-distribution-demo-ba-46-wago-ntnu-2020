import paho.mqtt.client as mqtt
from threading import Thread
from yr.libyr import Yr
import json
import time
import datetime


class YrForecastToHmi:
    """
    Using json file from yr.no to find forecast for 8 days.

    https://github.com/wckd/python-yr
    """

    def __init__(self):
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

    def importForcastLongFromYrInJson(self, place_string):
        """Import 8 days forcast from Yr.no in json file.

        Parameters:
        place_string (string): 
        The place to get the forecast from. 
        Format: "Land/Fylke/Kommune/Stedsnavn/"
        Example: "Norge/Trøndelag/Trondheim/Trondheim/"

        Returns:
        genarator:forecast 

        """

        self.json_yr_weather = Yr(location_name=place_string)
        forecast = self.json_yr_weather.forecast(as_json=True)
        return forecast

    def formatDataFromYrToJson(self, forecast_from_yr):
        """Find the usefull information in the json file and add the information to the right list.

        Parameters:
        forecast_from_yr (generator): 
        Use for loop to loop through the generator.

        Returns:
        formated_data_list (list):
        List of lists with formated data

        """

        for forecast in forecast_from_yr:
            forecast = json.loads(forecast)
            periode = int(forecast["@period"])
            from_time = forecast["@from"]
            to_time = forecast["@to"]
            symbol = forecast["symbol"]["@name"]
            temp = forecast["temperature"]["@value"]
            rain = forecast["precipitation"]["@value"]

            dateStr, weekday = self.jsonDateToWeekday(from_time)
            symbol_number = self.symbolStringToInt(symbol)

            if periode == 0 and self.flag == False:  # Find the first new period to set as new day.
                self.flag = True

            if self.flag == True and periode == 2:  # Using only period 2 for each day. 12:00-18:00.
                self.from_list.append(from_time)
                self.to_list.append(to_time)
                self.symbol_list.append(symbol)
                self.symbol_number_list.append(symbol_number)
                self.temp_list.append(temp)
                self.rain_list.append(rain)
                self.weekday_list.append(weekday)
                self.date_list.append(dateStr)

        formated_data_list = [
            self.from_list,
            self.to_list,
            self.symbol_list,
            self.symbol_number_list,
            self.temp_list,
            self.rain_list,
            self.weekday_list,
            self.date_list,
        ]
        return formated_data_list

    def jsonDateToWeekday(self, datetimestamp):
        """Change a date to a weekday in number. Mon:0, Tue:1, Wed:2, Thu:3, Fri:4, Sat:5, Sun:6

        Parameters:
        datetimestamp (str): 
        Format_YYYY-MM-DDTHH:MM:SS

        Returns:
        weekday (int):

        """

        dateStr = datetimestamp.split("T")[0]  # Split date from "dateTime"
        year, month, day = (int(x) for x in dateStr.split("-"))  # Convert date to right format
        weekday = datetime.date(year, month, day).weekday()  # Find weekday
        return dateStr, weekday

    def symbolStringToInt(self, symbol_string):
        """Change a symbol to a symbol number. Number given from list in init.

        Parameters:
        symbol_string (str): 

        Returns:
        symbol_number (int):

        """
        symbol_number = None
        for idx, weather_type in enumerate(
            self.weather_symbol_list
        ):  # Search list in weather_symbol_list to find weather type
            if symbol_string in weather_type:
                symbol_number = (
                    idx  # If found. Symbol number is index of the list in weather_symbol_list
                )
            if symbol_number == None:
                symbol_number = "Not found"  # If not found. Symbol number is "Not found". TODO: Endre til 3 i tilfellet værtypen ikke finnes.
        return symbol_number

    def mqttSend(self, formated_data):
        """Find the usefull information from list to send with MQTT

        Parameters:
        formated_data (list): 

        Returns:
        MQTT_send (dict):

        """
        symbol_number_list = formated_data[3]
        temp_list = formated_data[4]
        rain_list = formated_data[5]
        weekday_list = formated_data[6]

        MQTT_send = {
            "day1weekday": weekday_list[0],
            "day1symbol": symbol_number_list[0],
            "day1temp": temp_list[0],
            "day1rain": rain_list[0],
            "day2weekday": weekday_list[1],
            "day2symbol": symbol_number_list[1],
            "day2temp": temp_list[1],
            "day2rain": rain_list[1],
            "day3weekday": weekday_list[2],
            "day3symbol": symbol_number_list[2],
            "day3temp": temp_list[2],
            "day3rain": rain_list[2],
        }
        print(MQTT_send)
        return MQTT_send

    def getForecast(self):
        """ Main for forcast.

        Returns:
        MQTT_send (dict):
        """
        imported_data = self.importForcastLongFromYrInJson("Norge/Trøndelag/Trondheim/Trondheim/")
        formated_data = self.formatDataFromYrToJson(imported_data)
        send_data = self.mqttSend(formated_data)
        return send_data
