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
        self.__currentVolume_m3 = (self.__volume_m3 / 3) * 3  # 2/3 full at start
        # Can empty the water in 10 days
        self.__emissionValveMaxOpening_m3_per_s = self.__volume_m3 / (
            10.0 * self.__oneDayIsSimulatoedTo_s
        )

    def getWaterLevel_m(self):
        return self.__currentVolume_m3 / self.__area_m2

    def getWaterLevel_persent(self):
        return (self.getWaterLevel_m() / self.__hightMax_m) * 100.0

    def addCurrentRain_m_ToCurrentVolume(self, rain_m, rainPeriod_s):
        self.__currentVolume_m3 = self.__currentVolume_m3 + (
            ((rain_m / rainPeriod_s) * self.__area_m2) * self.__sampletime
        )

    def setWantedEmission_m3_per_s(self, emission_m3_per_s):
        newCurrentVolume_m3 = self.__currentVolume_m3 - (emission_m3_per_s * self.__sampletime)
        if newCurrentVolume_m3 < 0:
            self.__currentVolume_m3 = 0.0
        else:
            self.__currentVolume_m3 = newCurrentVolume_m3

    def emmissionValve_percent_ToFlow_m3_per_s(self, openingInPersent):
        return self.__emissionValveMaxOpening_m3_per_s * (openingInPersent / 100.0)
