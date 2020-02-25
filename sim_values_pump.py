import time
import random
from random import randint


class SimValuesPLS2:
    def __init__(self,):
        self.hoyde = 30  # m
        self.ror_diameter = 0.05  # m
        self.tetthet_vann = 1000  # kg/m^3
        self.tyngde_aks = 9.81  # m/s^2
        self.onsket_p = 5  # bar
        self.houses = 1000
        self.pump_running = [0, 0, 0]
        self.pump_running_value = [0, 0, 0]
        self.pump_running_manuel = [0, 0, 1]
        self.pump_running_value_manuel = [0, 100, 100]
        self.pump_current_draw = [0, 0, 0]
        self.pump_timer = [0, 0, 0]
        self.waterusage_person_day = (
            200  # l https://www.norskvann.no/index.php/vann/ofte-stilte-sporsmal-om-vann/91-forbruk
        )
        self.pump_pressure = 3  # bar
        self.p_out = 0
        self.timer_counter = 0
        self.auto_mode = [1, 0, 1]

    def waterLevel(self,):
        self.level = randint(1, 2)  # m

    def waterUsage(self,):
        self.random_users = randint(0, self.houses)
        self.waterusage_person_day = self.waterusage_person_day + random.uniform(-20, 20)
        self.water_usage_per_second = self.waterusage_person_day / (24 * 60 * 60)
        self.water_usage = self.water_usage_per_second * self.random_users
        self.water_usage = round(self.water_usage, 3)
        self.pressure_drop = 0.0005 * self.random_users
        self.waterusage_person_day = 200

    def pressureInPump(self,):
        self.p_in_pascal = self.tetthet_vann * self.tyngde_aks * (self.hoyde + self.level)
        self.p_in_bar = self.p_in_pascal / 100_000

    def manuelAuto(self,):
        for p in range(0, len(self.auto_mode)):

            if self.auto_mode[p] == 1:
                sim.PLS2(p)
            else:
                self.p_missing = self.onsket_p - self.p_in_bar + self.pressure_drop
                self.pump_running_value[p] = self.pump_running_value_manuel[p]

    def PLS2(self, p):
        self.p_missing = self.onsket_p - self.p_in_bar + self.pressure_drop

        if self.p_missing > 0:
            self.pump_running[p] = 1
        else:
            self.pump_running[p] = 0
        if (
            self.p_out - self.onsket_p > 0
            and sum(self.pump_running) > 0
            and self.pump_running_value[p] > 0
        ):
            self.pump_running_value[p] = self.pump_running_value[p] - 0.5
        elif self.p_out - self.onsket_p < 0 and sum(self.pump_running) > 0:
            self.pump_running_value[p] = self.pump_running_value[p] + 0.5

    def pressureOutPump(self,):
        self.p_out = self.p_in_bar + ((sum(self.pump_running_value) / 2) / 100) * (
            sum(self.pump_running) * self.pump_pressure
        )

    def flowOutPump(self,):
        pass

    def currentDrawPump(self,):
        for x in range(0, len(self.pump_running_value)):
            self.pump_current_draw[x] = round(self.pump_running_value[x] * 0.05, 2)

    def runtimePump(self,):
        if self.timer_counter == 5:
            for x in range(0, len(self.pump_running)):
                if self.pump_running[x] == 1 and self.pump_running_value[x] > 0:
                    self.pump_timer[x] += 1
                    self.timer_counter = 0

        self.timer_counter = self.timer_counter + 1

    def print(self,):
        print("Water usages: " + str(round(self.water_usage, 3)))
        print("Pressure in: " + str(round(self.p_in_bar, 3)))
        print("Pressure missing: " + str(round(self.p_missing, 2)))
        print("Pump running: " + str(self.pump_running))
        print("Pump value: " + str(self.pump_running_value))
        print("Pressure out: " + str(round(self.p_out, 2)))
        print("Current: " + str(self.pump_current_draw))
        print("Auto/Manuel A=1 " + str(self.auto_mode))
        print("Timer: " + str(self.timer_counter))
        print("Pump timer: " + str(self.pump_timer))
        print("")


sim = SimValuesPLS2()


while True:
    sim.waterUsage()
    sim.waterLevel()
    sim.pressureInPump()
    sim.manuelAuto()
    sim.pressureOutPump()
    sim.currentDrawPump()
    sim.runtimePump()
    sim.print()
    time.sleep(0.5)
