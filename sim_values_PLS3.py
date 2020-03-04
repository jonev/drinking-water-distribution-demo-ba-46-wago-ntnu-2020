from yr.libyr import Yr
import json
from random import randint
import random
import time


class SimValuesPLS3:
    def __init__(self,):
        # Solar panel and battery
        self.solar_weather_factor = [1, 0.8, 0.3, 0.15, 0, 0, 0, 0]
        self.solar_effect = 150  # watt
        self.solar_voltage = 12  # voltage
        self.battery_voltage = 12  # V
        self.battery_amphour = 26  # Ah
        self.battery_state_of_charge = self.battery_amphour / 2  # Startvalue
        self.sampling_time = 1
        self.samplings_in_hour = (60 * 60) / self.sampling_time
        # Weather
        self.symbol_equal_sun = ["Clear sky", "Fair"]  # 0
        self.symbol_equal_partly_cloudy = ["Partly cloudy"]  # 1
        self.symbol_equal_cloudy = ["Fog", "Cloudy"]  # 2
        self.symbol_equal_light_rain = [
            "Light rain",
            "Light rain showers",
            "Light sleet",
            "Light sleet showers",
            "Light rain showers and thunder",
            "Light sleet showers and thunder",
            "Light rain and thunder",
            "Light sleet and thunder",
        ]  # 3
        self.symbol_equal_rain = [
            "Rain showers",
            "Sleet",
            "Sleet showers",
            "Rain showers and thunder",
            "Sleet showers and thunder",
            "Rain and thunder",
            "Sleet and thunder",
        ]  # 4
        self.mye_regn = [
            "Heavy rain showers",
            "Heavy sleet",
            "Heavy sleet showers",
            "Heavy rain showers and thunder",
            "Heavy sleet showers and thunder",
            "Heavy rain and thunder",
            "Heavy sleet and thunder",
        ]  # 5
        self.symbol_equal_snow = [
            "Light symbol_equal_snow",
            "symbol_equal_snow",
            "Heavy symbol_equal_snow",
            "Light symbol_equal_snow showers",
            "symbol_equal_snow showers",
            "Heavy symbol_equal_snow showers",
            "Light symbol_equal_snow showers and thunder",
            "symbol_equal_snow showers and thunder",
            "Heavy symbol_equal_snow showers and thunder",
            "Light symbol_equal_snow and thunder",
            "symbol_equal_snow and thunder",
            "Heavy symbol_equal_snow and thunder",
        ]  # 6
        # FT values in pipes
        self.list_normal_water_consumption_hours = [
            8,
            6,
            5,
            5,
            5,
            5,
            5,
            6,
            7,
            7,
            8,
            9,
            9,
            9,
            9,
            10,
            11,
            12,
            12,
            12,
            11,
            11,
            10,
            8,
        ]
        self.list_hours = [
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
        ]
        self.zones_residens = [30, 50, 40, 60]
        self.pipes = [0, 0, 0, 0, 0, 0, 0]
        self.leak_in_pipe = [0, 0, 0, 0, 0, 0, 0]
        self.total_samples_every_hour = 10
        self.list_randomized_ft_value = []
        self.list_timestamp = []
        self.sample_nr = 0

    def importJsonDayForcast(self,):
        weather_type = Yr(location_name="Norge/Telemark/Skien/Skien")
        now = weather_type.now(as_json=True)
        forecast = json.loads(now)
        print(forecast)
        self.weather_symbol_list = int(forecast["@period"])
        self.from_time = forecast["@from"]
        self.to_time = forecast["@to"]
        self.symbol = forecast["symbol"]["@name"]
        self.temp = forecast["temperature"]["@value"]
        self.rain = forecast["precipitation"]["@value"]

        self.weather_symbol_list = [
            self.symbol_equal_sun,
            self.symbol_equal_partly_cloudy,
            self.symbol_equal_cloudy,
            self.symbol_equal_light_rain,
            self.symbol_equal_rain,
            self.mye_regn,
            self.symbol_equal_snow,
        ]
        for idx, self.weather_type in enumerate(self.weather_symbol_list):
            if self.symbol in self.weather_type:
                self.symbol_number = idx

    def solarPanelOutput(self,):
        print(self.symbol_number)
        self.battery_charging_value = (
            (self.solar_weather_factor[self.symbol_number] + random.uniform(0, 0.003))
            * self.solar_effect
            / self.solar_voltage
        )
        self.battery_charging_value_every_sampling = (
            self.battery_charging_value / self.samplings_in_hour
        )

    def batteryStateOfCharge(self,):
        self.battery_usage = round(random.uniform(1, 2), 2)  # amps
        self.battery_usage_every_sampling = self.battery_usage / self.samplings_in_hour
        self.charging = (
            self.battery_charging_value_every_sampling - self.battery_usage_every_sampling
        )
        if 0 < self.battery_state_of_charge < self.battery_amphour:
            self.battery_state_of_charge = self.battery_state_of_charge + self.charging
        else:
            self.battery_state_of_charge = self.battery_state_of_charge
        self.battery_value_persent = 100 * self.battery_state_of_charge / self.battery_amphour

        print("Battery Charging: " + str(round(self.battery_charging_value, 2)))
        print("Battery Output: " + str(round(self.battery_usage, 2)))
        print("Charging: " + str(round(self.charging, 5,)))
        print("Battery Value: " + str(round(self.battery_state_of_charge, 2)))
        print("Battery Value %: " + str(round(self.battery_value_persent, 2)))

    def flowInPipes(self,):
        for i in range(0, len(self.list_normal_water_consumption_hours)):
            self.list_normal_water_consumption_hours[i] = self.list_normal_water_consumption_hours[
                i
            ] * random.uniform(0.95, 1.05)
            self.ft_value = self.list_normal_water_consumption_hours[i]
            for m in range(0, self.total_samples_every_hour):
                if i < len(self.list_normal_water_consumption_hours) - 1:

                    # Interpolaring
                    self.start_ft_value_hour = self.list_normal_water_consumption_hours[i]
                    self.end_ft_value_hour = self.list_normal_water_consumption_hours[i + 1]
                    self.delta_ft_value_hour = self.end_ft_value_hour - self.start_ft_value_hour
                    self.dif_ft_value = self.delta_ft_value_hour / self.total_samples_every_hour
                    self.ft_value = self.ft_value + self.dif_ft_value
                    #

                    self.randomized_ft_value = self.ft_value * random.uniform(0.95, 1.05)

                    self.list_randomized_ft_value.append(round(self.randomized_ft_value, 2))
                    self.sample_nr = self.sample_nr + 1
                    self.list_timestamp.append(self.sample_nr)

                    # Plotting
                    # plt.plot(self.list_timestamp, self.list_randomized_ft_value, c=numpy.random.rand(3,))
                    # plt.show()

                    # Ft in pipes
                    self.pipes[0] = (
                        round(self.zones_residens[0] * self.randomized_ft_value, 2)
                        + self.leak_in_pipe[0]
                    )
                    self.pipes[1] = (
                        round(self.zones_residens[1] * self.randomized_ft_value, 2)
                        + self.leak_in_pipe[1]
                    )
                    self.pipes[2] = (
                        round(self.zones_residens[2] * self.randomized_ft_value, 2)
                        + self.leak_in_pipe[2]
                    )
                    self.pipes[3] = (
                        round(self.zones_residens[3] * self.randomized_ft_value, 2)
                        + self.leak_in_pipe[3]
                    )
                    self.pipes[4] = round(self.pipes[3] + self.pipes[2], 2) + self.leak_in_pipe[4]
                    self.pipes[5] = round(self.pipes[4] + self.pipes[1], 2) + self.leak_in_pipe[5]
                    self.pipes[6] = round(self.pipes[0] + self.pipes[5], 2) + self.leak_in_pipe[6]

                    sim.importJsonDayForcast()
                    sim.solarPanelOutput()
                    sim.batteryStateOfCharge()

                    print("Flow in pipes: " + str(self.pipes))
                    print("Randomized flow value: " + str(round(self.randomized_ft_value, 2)))
                    time.sleep(2)

    def samplingTime(self,):
        time.sleep(self.sampling_time)


sim = SimValuesPLS3()
while True:
    sim.importJsonDayForcast()
    # sim.solarPanelOutput()
    # sim.batteryStateOfCharge()
    # sim.samplingTime()
    sim.flowInPipes()
    """
    print(weather_type)
    print(weather_symbol_list)
    print(from_time)
    print(to_time)
    print(symbol)
    print(temp)
    print(rain)
    """
