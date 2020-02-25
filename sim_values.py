from plclib.mqtt_client import MQTTClient
from threading import Thread
from random import randint
import time
import json

# http://www.hivemq.com/demos/websocket-client/
mqtt = MQTTClient("broker.hivemq.com", 1883, 60, ["wago/ba/sim/#"])
mqttThread = Thread(target=mqtt.loopForever, args=())
mqttThread.start()
time.sleep(2)


class SimulatingValues:
    """
    This class make random weather, rain and find the waterlevel.  
    """

    def __init__(self,):
        """
        Initialize the attributes of the class
        """
        self.valve = 0
        self.outflow = 7  # Flow when emission valve is open
        self.level = 80  # The water level to start with
        self.weatherTypes = [
            ("sun", -1, -1),
            ("partlycloudy", 0, 0),
            ("cloudy", 0, 0),
            ("drizzle", 2, 3),
            ("rainy", 4, 5),
            ("storm", 6, 7),
        ]  # List of weathertypes and the (min,max) rain for each weathertypes
        self.random = int(len(self.weatherTypes) / 2)  # Startvalue for random weather

    def randomWeather(self,):
        """Find a random weather
        
        :return: [random weather from weathertypes]
        :rtype: [str]
        """
        self.random = self.random + randint(-1, 2)  # Logic so the weather gradually change
        if self.random >= len(self.weatherTypes):  # Avoid the number to go out of range
            self.random = len(self.weatherTypes) - 1
        elif self.random < 0:  # Avoid the number to go out of range
            self.random = 0
        self.weather = self.weatherTypes[self.random][0]  # Choose the weather from the random value
        print(self.weather)
        return self.weather

    def rainWeather(self):
        """Find the amount of rain from the weathertype 
        
        :return: [rain in mm]
        :rtype: [int]
        """
        mini = self.weatherTypes[self.random][1]
        maxi = self.weatherTypes[self.random][2]
        self.rain = randint(mini, maxi)
        print(self.rain)
        return self.rain

    def waterLevel(self):
        """Find the waterlevel in the tank affected by the weather and rain
        
        :return: [water level]
        :rtype: [int]
        """
        self.level = self.level + self.rain  # Water level increases if its raining
        print(self.level)
        return self.level

    def valveOpen(self):
        """Reduces the water level if the valve is open
        """
        if self.valve == 1:
            self.level = self.level - self.outflow


simulationValues = SimulatingValues()
while True:
    """Sending values with MQTT to broker.
    """

    randomWeather = simulationValues.randomWeather()
    rain = simulationValues.rainWeather()
    waterLevel = simulationValues.waterLevel()
    simulationValues.randomWeather()
    simulationValues.rainWeather()
    simulationValues.waterLevel()
    # simulationValues.valveOpen()
    # mqtt.publish("wago/ba/sim/out/randomWeather", randomWeather.__str__())
    # mqtt.publish("wago/ba/sim/out/rain", rain.__str__())
    dict_ = {"waterLevel": waterLevel, "rain": rain, "randomWeather": randomWeather}  # Jone
    mqtt.publish("wago/ba/sim/out/waterLevel", json.dumps(dict_))  # Jone

    time.sleep(5)

