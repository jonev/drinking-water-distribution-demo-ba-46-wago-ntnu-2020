from threading import Thread
from random import randint
import time
import json

# http://www.hivemq.com/demos/websocket-client/
mqtt = MQTTClient("broker.hivemq.com", 1883, 60, ["wago/ba/sim/#"])
mqttThread = Thread(target=mqtt.loopForever, args=())
mqttThread.start()
time.sleep(2)


class SimValuesPLS1:
    """
    This class make weather_index weather, rain and find the waterlevel.  
    """

    def __init__(self,):
        """
        Initialize the attributes of the class
        """
        self.emission_valve_percen_open = 0
        self.water_emission_flow = 7  # Flow when emission emission_valve_percen_open is open
        self.water_level = 80  # The water water_level to start with
        self.weather_type_simulated = [
            ("sun", -1, -1),
            ("partlycloudy", 0, 0),
            ("cloudy", 0, 0),
            ("drizzle", 2, 3),
            ("rainy", 4, 5),
            ("storm", 6, 7),
        ]  # List of weather_type_simulated and the (min,max) rain for each weather_type_simulated
        self.weather_index = int(
            len(self.weather_type_simulated) / 2
        )  # Startvalue for weather_index weather

    def randomWeather(self,):
        """Find a weather_index weather
        
        :return: [weather_index weather from weather_type_simulated]
        :rtype: [str]
        """
        self.weather_index = self.weather_index + randint(
            -1, 2
        )  # Logic so the weather gradually change
        if self.weather_index >= len(
            self.weather_type_simulated
        ):  # Avoid the number to go out of range
            self.weather_index = len(self.weather_type_simulated) - 1
        elif self.weather_index < 0:  # Avoid the number to go out of range
            self.weather_index = 0
        self.weather = self.weather_type_simulated[self.weather_index][
            0
        ]  # Choose the weather from the weather_index value
        print(self.weather)
        return self.weather

    def randomRain(self):
        """Find the amount of rain from the weathertype 
        
        :return: [rain in mm]
        :rtype: [int]
        """
        min_rain = self.weather_type_simulated[self.weather_index][1]
        max_rain = self.weather_type_simulated[self.weather_index][2]
        self.rain = randint(min_rain, max_rain)
        print(self.rain)
        return self.rain

    def waterLevel(self):
        """Find the waterlevel in the tank affected by the weather and rain
        
        :return: [water water_level]
        :rtype: [int]
        """
        self.water_level = (
            self.water_level + self.rain
        )  # Water water_level increases if its raining
        print(self.water_level)
        return self.water_level

    def emissionValveOpen(self):
        """Reduces the water water_level if the emission_valve_percen_open is open
        """
        if self.emission_valve_percen_open == 1:
            self.water_level = self.water_level - self.water_emission_flow


sim = SimValuesPLS1()
while True:
    """Sending values with MQTT to broker.
    """

    randomWeather = sim.randomWeather()
    rain = sim.randomRain()
    waterLevel = sim.waterLevel()
    sim.randomWeather()
    sim.randomRain()
    sim.waterLevel()
    # Denne må du ikke kalle før du vett at der er data som har blitt mottat
    # Eller må du gjøre "getData" sikker mot at noen prøver å hente ut data som ikke fins

    # simulationValues.emissionValveOpen()
    # mqtt.publish("wago/ba/sim/out/randomWeather", randomWeather.__str__())
    # mqtt.publish("wago/ba/sim/out/rain", rain.__str__())
    dict_ = {"waterLevel": waterLevel, "rain": rain, "randomWeather": randomWeather}  # Jone
    mqtt.publish("wago/ba/sim/out/waterLevel", json.dumps(dict_))  # Jone
    # print(self.on_message)
    time.sleep(5)

