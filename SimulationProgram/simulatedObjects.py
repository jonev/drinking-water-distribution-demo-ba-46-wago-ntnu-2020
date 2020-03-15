class Water:
    """ Object representing the water
        USING SI units https://en.wikipedia.org/wiki/International_System_of_Units
    """

    def __init__(self, sampletime, oneDayIsSimulatedTo_s):
        self.__sampletime = sampletime
        self.__oneDayIsSimulatoedTo_s = oneDayIsSimulatedTo_s
        self.__length_m = 1000.0
        self.__width_m = 1000.0
        self.__hightMax_m = 100.0
        self.__area_m2 = self.__length_m * self.__width_m
        self.__volume_m3 = self.__area_m2 * self.__hightMax_m
        self.__currentVolume_m3 = (self.__volume_m3 / 3) * 2  # 2/3 full at start
        # Can empty the water in 10 days
        self.__emissionValveMaxOpening_m3_per_s = self.__volume_m3 / (
            10.0 * self.__oneDayIsSimulatoedTo_s
        )
        self.__inflowFromRivers_m3_per_s = self.__emissionValveMaxOpening_m3_per_s / 5

    def getWaterLevel_m(self):
        return self.__currentVolume_m3 / self.__area_m2

    def getWaterLevel_percent(self):
        return (self.getWaterLevel_m() / self.__hightMax_m) * 100.0

    def addCurrentRain_m_ToCurrentVolume(self, rain_m, rainPeriod_s):
        self.__currentVolume_m3 = self.__currentVolume_m3 + (
            ((rain_m / rainPeriod_s) * self.__area_m2) * self.__sampletime
        )

    def addInflowFromRivers(self):
        self.__currentVolume_m3 = self.__currentVolume_m3 + (
            self.__inflowFromRivers_m3_per_s * self.__sampletime
        )

    def setWantedEmission_m3_per_s(self, emission_m3_per_s):
        newCurrentVolume_m3 = self.__currentVolume_m3 - (emission_m3_per_s * self.__sampletime)
        if newCurrentVolume_m3 < 0:
            self.__currentVolume_m3 = 0.0
        else:
            self.__currentVolume_m3 = newCurrentVolume_m3

    def emmissionValve_percent_ToFlow_m3_per_s(self, openingInPersent):
        return self.__emissionValveMaxOpening_m3_per_s * (openingInPersent / 100.0)


class RainForcast:
    def __init__(self, sampletime, oneDayIsSimulatedTo_s, rainForcast_m_per_day):
        self.__sampletime = sampletime
        self.__oneDayIsSimulatoedTo_s = oneDayIsSimulatedTo_s
        self.__rainForcast_m_per_day = rainForcast_m_per_day
        self.__start = 0
        self.__day = 0
        self.__rain = 0

    def getForcast(self):
        return (
            self.__rainForcast_m_per_day[self.__day :] + self.__rainForcast_m_per_day[: self.__day]
        )

    def calculateRain(self):
        rain = (
            self.__rainForcast_m_per_day[self.__day] / self.__oneDayIsSimulatoedTo_s
        ) * self.__sampletime
        self.__start = self.__start + self.__sampletime
        if self.__start >= self.__oneDayIsSimulatoedTo_s:
            self.__day = self.__day + 1
            self.__start = self.__start - self.__oneDayIsSimulatoedTo_s
        if self.__day >= len(self.__rainForcast_m_per_day):
            self.__day = 0
        self.__rain = rain

    def getRain_m(self):
        return self.__rain
