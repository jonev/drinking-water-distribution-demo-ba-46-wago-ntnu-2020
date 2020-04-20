from yr.libyr import Yr
from random import randint
import random
import json
import time


class BatteryLevel:
    def __init__(self):

        self.solar_effect = [100.0, 100.0, 100.0]  # Watt
        self.solar_voltage = [24.0, 24.0, 24.0]  # Voltage
        self.battery_voltage = [24.0, 24.0, 24.0]  # Voltage
        self.battery_amphour = [20.0, 20.0, 20.0]  # Ah
        self.battery_start_level = [14.44, 12.32, 17.23]  # Ah
        self.solar_weather_factor = [1.0, 0.8, 0.3, 0.15, 0.1, 0.1]
        self.battery_output = [1.0, 1.0, 1.0]
        self.solar_panel_output = [0, 0, 0]

        self.secounds_one_hour = 86400
        self.sampling_time_sec = 2.4
        self.total_samples_one_hour = self.secounds_one_hour / self.sampling_time_sec

        self.battery_level = self.battery_start_level

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

    def importForcastTodayFromYrInJson(self, place_string):
        """Import 8todays forcast from Yr.no in json file.

        Parameters:
        place_string (string): 
        The place to get the forecast from. 
        Format: "Land/Fylke/Kommune/Stedsnavn/"
        Example: "Norge/Trøndelag/Trondheim/Trondheim/"

        Returns:
        genarator:forecast 

        """

        weather_import = Yr(location_name=place_string)
        weather_now_json = weather_import.now(as_json=True)
        weather_now = json.loads(weather_now_json)
        print(weather_now)
        return weather_now

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

    def solarPanelOutput(self, symbol_number):
        """Calculate the solar panale output by given weathertype
        Parameters:
        symbol_number (int)

        Returns:
        solar_panel_output (list):
        List of solar panel output. 
        Each index in the list indicate Amps from solar panel in one module.

        """
        for module_number in range(0, len(self.battery_voltage)):
            self.solar_panel_output[module_number] = (
                self.solar_weather_factor[symbol_number] * self.solar_effect[module_number]
            )  # Find the effect from solarpanel given by weathertype
            self.solar_panel_output[module_number] = (
                self.solar_panel_output[module_number] / self.solar_voltage[module_number]
            )  # Find output from solarpanel in Amps
            self.solar_panel_output[module_number] = round(
                self.solar_panel_output[module_number] * random.uniform(0.95, 1.05), 3
            )  # To get a slightly varied value we multiply the result with a randomized factor
        return self.solar_panel_output

    def batteryOutput(self):
        """The battery output is already calculated and set as a parameter in init.
        Parameters:

        Returns:
        battery_output (list):
        List of battery_output output. 
        Each index in the list indicate Amps out from battery in one module

        """
        for module_number in range(0, len(self.battery_voltage)):
            self.battery_output[module_number] = round(
                self.battery_output[module_number] * random.uniform(0.95, 1.05), 3
            )  # To get a slightly varied value we multiply the result with a randomized factor
        return self.battery_output

    def calculateBatteryLevel(self, solar_panel_output, battery_output):
        """Calcualte the battery level by given output and input.

        Parameters:
        solar_panel_output (list) 
        battery_output (list) 

        Returns:
        battery_level (list):
        Each index in the list indicate Ah in battery in a module

        """
        for module_number in range(0, len(self.battery_voltage)):
            self.battery_level[module_number] = round(
                self.battery_level[module_number]
                + (solar_panel_output[module_number] - battery_output[module_number])
                / self.total_samples_one_hour,
                3,
            )  # Have to devide on total_samples_one_hour. So we get one Ah after the program have run as many times as total_samples_one_hour since the input and output is in Amps and not Ah.
            if self.battery_level[module_number] < 0:
                self.battery_level[module_number] = 0
            elif self.battery_level[module_number] > self.battery_amphour[module_number]:
                self.battery_level[module_number] = self.battery_amphour[module_number]
            # Ensure that battery level doesnt go over or under max and min value.
        return self.battery_level

    def mqttSend(self, solar_panel_output, battery_output, battery_level):
        MQTT_send = {
            "CI01": round(solar_panel_output[0], 2),
            "CO01": round(battery_output[0], 2),
            "BL01": round(battery_level[0], 2),
            "CI02": round(solar_panel_output[1], 2),
            "CO02": round(battery_output[1], 2),
            "BL02": round(battery_level[1], 2),
            "CI03": round(solar_panel_output[2], 2),
            "CO03": round(battery_output[2], 2),
            "BL03": round(battery_level[2], 2),
        }
        return MQTT_send

    def getBatteryLevelValues(self):
        """ Main for BatteryLevel.

        Returns:
        MQTT_send (dict):
        """
        imported_weather = self.importForcastTodayFromYrInJson(
            "Norge/Trøndelag/Trondheim/Trondheim/"
        )
        weather_symbol = imported_weather["symbol"]["@name"]
        # print(weather_symbol)
        weather_number = self.symbolStringToInt(weather_symbol)
        # print(weather_number)
        solar_panel_output = self.solarPanelOutput(weather_number)
        # print("Solar" + str(solar_panel_output))
        battery_output = self.batteryOutput()
        # print("Battery" + str(battery_output))
        battery_level = self.calculateBatteryLevel(solar_panel_output, battery_output)
        # print("LEvel" + str(battery_level))
        return self.mqttSend(solar_panel_output, battery_output, battery_level)
