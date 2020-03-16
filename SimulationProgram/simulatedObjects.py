import copy


class Water:
    """ Object representing the water
        USING SI units https://en.wikipedia.org/wiki/International_System_of_Units
    """

    def __init__(self, sampletime_s, oneDayIsSimulatedTo_s):
        self.__sampletime_s = sampletime_s
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
            ((rain_m / rainPeriod_s) * self.__area_m2) * self.__sampletime_s
        )

    def addInflowFromRivers(self):
        self.__currentVolume_m3 = self.__currentVolume_m3 + (
            self.__inflowFromRivers_m3_per_s * self.__sampletime_s
        )

    def setWantedEmission_m3_per_s(self, emission_m3_per_s):
        newCurrentVolume_m3 = self.__currentVolume_m3 - (emission_m3_per_s * self.__sampletime_s)
        if newCurrentVolume_m3 < 0:
            self.__currentVolume_m3 = 0.0
        else:
            self.__currentVolume_m3 = newCurrentVolume_m3

    def emmissionValve_percent_ToFlow_m3_per_s(self, openingInPersent):
        return self.__emissionValveMaxOpening_m3_per_s * (openingInPersent / 100.0)


class RainForcast:
    def __init__(self, sampletime_s, oneDayIsSimulatedTo_s, rainForcast_m_per_day):
        self.__sampletime_s = sampletime_s
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
        ) * self.__sampletime_s
        self.__start = self.__start + self.__sampletime_s
        if self.__start >= self.__oneDayIsSimulatoedTo_s:
            self.__day = self.__day + 1
            self.__start = self.__start - self.__oneDayIsSimulatoedTo_s
        if self.__day >= len(self.__rainForcast_m_per_day):
            self.__day = 0
        self.__rain = rain

    def getRain_m(self):
        return self.__rain


class WaterDistributionPipes:
    def __init__(self, sampletime_s, oneDayIsSimulatedTo_s):
        self.__sampletime_s = sampletime_s
        self.__oneDayIsSimulatoedTo_s = oneDayIsSimulatedTo_s
        self.__normalWaterConsumption_l_hour_PerHour = [
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
        self.__normalWaterConsumption_l_hour_Per5sSample = [
            7,
            5,
            5,
            5.5,
            7,
            8.5,
            9,
            9.5,
            11.5,
            12,
            11,
            9,
        ]
        self.__normalWaterConsumption_l_hour_PerDbSample = [
            8,
            7.5,
            7.0,
            6.5,
            6,
            6.75,
            6.5,
            6.25,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5,
            5.25,
            5.5,
            5.75,
            6,
            6.25,
            6.5,
            6.75,
            7,
            7,
            7,
            7,
            7,
            7.25,
            7.5,
            7.75,
            8,
            8.25,
            8.5,
            8.75,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9,
            9.25,
            9.5,
            9.75,
            10,
            10.25,
            10.5,
            10.75,
            11,
            11.25,
            11.5,
            11.75,
            12,
            12,
            12,
            12,
            12,
            12,
            12,
            12,
            12,
            11.75,
            11.5,
            11.25,
            11,
            11,
            11,
            11,
            11,
            11.75,
            11.5,
            11.25,
            10,
            9.5,
            9,
            8.5,
            8,
            8,
            8,
            8,
        ]
        self.__zonesResidents = [30, 50, 40, 60]
        self.__flowInPipe = [0, 0, 0, 0, 0, 0, 0]
        self.__leakInPipe = [0, 0, 0, 0, 0, 0, 0]
        self.__samples_5s = 0

    def __calulateFlowInPipes(self, zonesResidents, normalWaterConsumption, sample, leakInPipe):
        # Pipes at the end
        flowInPipe = [0, 0, 0, 0, 0, 0, 0]

        flowInPipe[0] = (zonesResidents[0] * normalWaterConsumption[sample]) + leakInPipe[0]
        flowInPipe[1] = (zonesResidents[1] * normalWaterConsumption[sample]) + leakInPipe[1]
        flowInPipe[2] = (zonesResidents[2] * normalWaterConsumption[sample]) + leakInPipe[2]
        flowInPipe[3] = (zonesResidents[3] * normalWaterConsumption[sample]) + leakInPipe[3]
        # Pipes not at the end
        flowInPipe[4] = flowInPipe[3] + flowInPipe[2] + leakInPipe[4]
        flowInPipe[5] = flowInPipe[4] + flowInPipe[1] + leakInPipe[5]
        flowInPipe[6] = flowInPipe[0] + flowInPipe[5] + leakInPipe[6]
        return flowInPipe

    def calculateFlowInPipesNow(self):
        self.__samples_5s = self.__samples_5s + 1
        if self.__samples_5s >= 12:
            self.__samples_5s = 0
        self.__flowInPipe = self.__calulateFlowInPipes(
            self.__zonesResidents,
            self.__normalWaterConsumption_l_hour_Per5sSample,
            self.__samples_5s,
            self.__leakInPipe,
        )

    def calculateFlowInPipesSinceLastSample(self, timestamp):
        # One sample is 2 hours -> 8 samples
        flowValues = []
        timestamps = []
        for index in range(8):
            flowInPipes = self.__calulateFlowInPipes(
                self.__zonesResidents,
                self.__normalWaterConsumption_l_hour_PerDbSample,
                ((self.__samples_5s) * 8) + (8 - index),
                self.__leakInPipe,
            )
            flowValues.append(flowInPipes)
            timestamps.append(timestamp)  # TODO legg til litt tid på hver

        return flowValues, timestamps

    def getFlowInPipes(self):
        return copy.deepcopy(self.__flowInPipe)
