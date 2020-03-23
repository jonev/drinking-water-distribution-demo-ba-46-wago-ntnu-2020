import copy
import datetime
import random
import logging


class Water:
    """ Object representing the water
        USING SI units https://en.wikipedia.org/wiki/International_System_of_Units
    """

    def __init__(self, sampletime_s, oneDayIsSimulatedTo_s, length_m, width_m, hightMax_m):
        self.__sampletime_s = sampletime_s
        self.__oneDayIsSimulatoedTo_s = oneDayIsSimulatedTo_s
        self.__length_m = length_m
        self.__width_m = width_m
        self.__hightMax_m = hightMax_m
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

    def emissionValve_percent_ToFlow_m3_per_s(self, openingInPersent):
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
    def __init__(self, sampletime_s, oneDayIsSimulatedTo_s, simulatedSamplesPerDay):
        if oneDayIsSimulatedTo_s % sampletime_s != 0:
            raise Exception("One day must be simulated to a multiplum of the sampletime")
        self.__sampletime_s = sampletime_s
        self.__oneDayIsSimulatoedTo_s = oneDayIsSimulatedTo_s
        self.__samplesPerDay = oneDayIsSimulatedTo_s // sampletime_s
        self.__simulatedSampelsPerSample = simulatedSamplesPerDay // self.__samplesPerDay
        # Base - from a source online
        self.__normalWaterConsumptionForADay_Per_Hour_24_samples = [
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

        self.__normalWaterConsumptionForASimulatedDayWithHistoricallyData = self.__scaleNormalWaterComsumptionForADay(
            self.__normalWaterConsumptionForADay_Per_Hour_24_samples, simulatedSamplesPerDay
        )
        self.__normalWaterConsumptionForASimulatedDay_Per_Hour = self.__scaleNormalWaterComsumptionForADay(
            self.__normalWaterConsumptionForADay_Per_Hour_24_samples, self.__samplesPerDay
        )
        self.__zonesResidents = [30, 50, 40, 60]
        self.__flowInPipe = [0, 0, 0, 0, 0, 0, 0]
        self.__leakInPipe = [0, 0, 0, 0, 0, 0, 0]
        self.__samplesCounter = 0
        self.__leakInterval = self.__oneDayIsSimulatoedTo_s * 3
        self.__leakIntervalCounter = 0

    def __scaleNormalWaterComsumptionForADay(self, inputlist, wantedLength):
        l = inputlist.__len__()

        result = []
        if wantedLength <= l:
            if l % wantedLength != 0:
                raise Exception("Wanted length must be a multiplum of 24")
            steps = l // wantedLength
            for i in range(wantedLength):
                result.append(inputlist[i * steps])
        else:
            if wantedLength % l != 0:
                raise Exception("Wanted length must be a multiplum of 24")
            stepSize = l / wantedLength
            samplesPrSample = wantedLength // l
            for b in range(l):
                releation = inputlist[(b + 1) % l] - inputlist[b]
                for s in range(samplesPrSample):
                    sample = inputlist[b] + (releation * (s * stepSize))
                    result.append(sample)
        return result

    def __calulateFlowInPipes(self, zonesResidents, normalWaterConsumption, sample, leakInPipe):
        # Pipes at the end
        flowInPipe = [0, 0, 0, 0, 0, 0, 0]

        flowInPipe[0] = (
            zonesResidents[0] * normalWaterConsumption[sample] * random.uniform(0.95, 1.05)
        ) + leakInPipe[0]
        flowInPipe[1] = (
            zonesResidents[1] * normalWaterConsumption[sample] * random.uniform(0.95, 1.05)
        ) + leakInPipe[1]
        flowInPipe[2] = (
            zonesResidents[2] * normalWaterConsumption[sample] * random.uniform(0.95, 1.05)
        ) + leakInPipe[2]
        flowInPipe[3] = (
            zonesResidents[3] * normalWaterConsumption[sample] * random.uniform(0.95, 1.05)
        ) + leakInPipe[3]
        # Pipes not at the end
        flowInPipe[4] = flowInPipe[3] + flowInPipe[2] + leakInPipe[4]
        flowInPipe[5] = flowInPipe[4] + flowInPipe[1] + leakInPipe[5]
        flowInPipe[6] = flowInPipe[0] + flowInPipe[5] + leakInPipe[6]
        return flowInPipe

    def calculateFlowInPipesNow(self):
        self.__samplesCounter = self.__samplesCounter + 1
        if self.__samplesCounter >= self.__samplesPerDay:
            self.__samplesCounter = 0
        self.__leakIntervalCounter = self.__leakIntervalCounter + self.__sampletime_s
        if self.__leakIntervalCounter > self.__leakInterval:
            self.__leakIntervalCounter = 0
            if self.__leakInPipe[0] == 0:
                self.__leakInPipe[0] = 100
                logging.info("Leak activated")
            else:
                self.__leakInPipe[0] = 0
                logging.info("Leak de-activated")

        self.__flowInPipe = self.__calulateFlowInPipes(
            self.__zonesResidents,
            self.__normalWaterConsumptionForASimulatedDay_Per_Hour,
            self.__samplesCounter,
            self.__leakInPipe,
        )

    def getFlowInPipesSinceLastSample(self, datetimestamp):
        # One sample is 2 hours -> 8 samples
        flowValues = []
        datetimestamps = []
        timeBetweenSamples = self.__sampletime_s / self.__simulatedSampelsPerSample
        for index in range(self.__simulatedSampelsPerSample):
            sample = (
                ((self.__samplesCounter) * self.__simulatedSampelsPerSample) - 7 + index
            ) % self.__normalWaterConsumptionForASimulatedDayWithHistoricallyData.__len__()

            flowInPipes = self.__calulateFlowInPipes(
                self.__zonesResidents,
                self.__normalWaterConsumptionForASimulatedDayWithHistoricallyData,
                sample,
                self.__leakInPipe,
            )

            flowValues.append(flowInPipes)
            datetimestamps.append(
                datetimestamp - datetime.timedelta(seconds=(7 - index) * timeBetweenSamples)
            )

        return flowValues, datetimestamps

    def getFlowInPipes(self):
        return copy.deepcopy(self.__flowInPipe)
