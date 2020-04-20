from plclib.mqtt_client import MQTTClient
from threading import Thread
from random import randint
import random
import time
import json

mqtt = MQTTClient("broker.hivemq.com", 1883, 60, ["wago/ba/sim/#"])
mqttThread = Thread(target=mqtt.loopForever, args=())
mqttThread.start()
time.sleep(2)


class SimValuesPLS2:
    def __init__(self,):
        self.water_source_height = 30  # m
        self.density_water = 1000  # kg/m^3
        self.gravitational_acc = 9.81  # m/s^2

        self.number_of_consumers = 300
        self.waterusage_person_day = 200  # l https://www.norskvann.no/index.php/vann/ofte-stilte-sporsmal-om-vann/91-forbruk)

        # Fra HMI
        self.pump_running = [0, 0, 0]
        self.pump_running_value = [0, 0, 0]

        self.pump_current_draw = [0, 0, 0]
        self.pump_timer = [0, 0, 0]

        self.pump_pressure = 3  # bar
        self.pressure_out = 0

        # For og simulere manuel auto
        self.auto_mode = [1, 1, 0]  # Auto(1) Manuell (0)
        self.pump_manuel_start_stopp = [0, 0, 1]  # Start(1) Stopp(0)
        self.pump_running_manuel_value = [0, 0, 20]  # 0-100
        self.onsket_p = 5  # bar

        self.number_of_pumps = len(self.auto_mode)

    def waterLevel(self,):
        self.level = randint(1, 2)  # m

    def waterUsage(self,):
        self.random_number_of_consumers = randint(0, self.number_of_consumers)
        self.waterusage_person_day = self.waterusage_person_day + random.uniform(-20, 20)
        self.waterusage_person_per_second = self.waterusage_person_day / (24 * 60 * 60)
        self.water_usage = self.waterusage_person_per_second * self.random_number_of_consumers
        self.water_usage = round(self.water_usage, 3)
        self.pressure_drop = 0.00005 * self.random_number_of_consumers
        self.waterusage_person_day = 200
        return self.water_usage

    def pressureInPumpStation(self,):
        self.pressure_in_pascal = (
            self.density_water * self.gravitational_acc * (self.water_source_height + self.level)
        )
        self.pressure_in_bar = self.pressure_in_pascal / 100_000
        return self.pressure_in_bar

    def manuelAuto(self,):  # Fjernes når man får verdier fra PLS
        self.p_missing = self.onsket_p + self.pressure_drop - self.pressure_out
        for self.pump in range(0, self.number_of_pumps):
            if self.auto_mode[self.pump] == 1:
                sim.PLS2()
            else:
                sim.manuel()

    def PLS2(self,):  # Fjernes når man får verdier fra PLS

        if self.p_missing > 0:
            self.pump_running[self.pump] = 1
            self.pump_running_value[self.pump] = self.pump_running_value[self.pump] + 0.1
        elif self.p_missing < 0 and self.pump_running_value[self.pump] > 0:
            self.pump_running_value[self.pump] = self.pump_running_value[self.pump] - 0.1

        else:
            self.pump_running[self.pump] = 0

    def manuel(self,):  # Fjernes når man får verdier fra PLS
        if (
            self.pump_manuel_start_stopp[self.pump] == 1
            and self.pump_running_manuel_value[self.pump] > 0
        ):
            self.pump_running[self.pump] = 1
            self.pump_running_value[self.pump] = self.pump_running_manuel_value[self.pump]
        else:
            self.pump_running[self.pump] = 0
            self.pump_running_value[self.pump] = 0

    def pressureOutPumpStation(self,):
        self.pressure_out = (
            self.pressure_in_bar + (sum(self.pump_running_value) / 100) * self.pump_pressure
        )
        return self.pressure_out

    def flowOutPumpStation(self,):
        self.flow_out = self.water_usage

    def currentDrawPump(self,):
        for pump in range(0, self.number_of_pumps):
            self.pump_current_draw[pump] = round(self.pump_running_value[pump] * 0.05, 2)
        return self.pump_current_draw

    def runtimePump(self,):
        for pump in range(0, self.number_of_pumps):
            if self.pump_running[pump] == 1:
                self.pump_timer[pump] += 1
        return self.pump_timer

    def print(self,):
        print("Water usages: " + str(round(self.water_usage, 3)))
        print("Pressure in: " + str(round(self.pressure_in_bar, 3)))
        print("Pressure missing: " + str(round(self.p_missing, 2)))
        print("Pump running: " + str(self.pump_running))
        print("Pump value: " + str(self.pump_running_value))
        print("Pressure out: " + str(round(self.pressure_out, 2)))
        print("Current: " + str(self.pump_current_draw))
        print("Auto/Manuel A=1 " + str(self.auto_mode))
        print("Pump timer: " + str(self.pump_timer))
        print("")


sim = SimValuesPLS2()

while True:
    # MQTT IN
    # data = mqtt.getData("wago/ba/sim/inn/test")
    # objectJson = json.loads(data)

    waterUsage = sim.waterUsage()
    sim.waterLevel()
    pressureInPumpStation = sim.pressureInPumpStation()
    sim.manuelAuto()
    pressureOutPumpStation = sim.pressureOutPumpStation()
    currentDrawPump = sim.currentDrawPump()
    runtimePump = sim.runtimePump()
    sim.print()

    # MQTT OUT

    dict_ = {
        "waterUsage": waterUsage,
        "pressureInPumpStation": pressureInPumpStation,
        "pressureOutPumpStation": pressureOutPumpStation,
        "pumpCurrent": currentDrawPump,
        "runtimePump": runtimePump,
    }
    mqtt.publish("wago/ba/sim/out/PLS2", json.dumps(dict_))
    time.sleep(2)
