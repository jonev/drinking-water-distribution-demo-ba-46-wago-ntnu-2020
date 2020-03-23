import unittest
from ddt import ddt, data, unpack

from SimulationProgram.simulatedObjects import Water, RainForcast, WaterDistributionPipes


@ddt
class SimulatedObjectsTests(unittest.TestCase):
    # TODO add more datarows
    @data((5, 60, 1000.0, 1000.0, 100.0, (100.0 / 3) * 2))
    @unpack
    def test_water_levels(
        self, sampletime_s, oneDayIsSimulatedTo_s, length_m, width_m, hightMax_m, expectedHight_m
    ):
        w = Water(sampletime_s, oneDayIsSimulatedTo_s, length_m, width_m, hightMax_m)

        self.assertAlmostEqual(expectedHight_m, w.getWaterLevel_m(), places=3)
        expectedHight_percent = (w.getWaterLevel_m() / hightMax_m) * 100.0
        self.assertAlmostEqual(expectedHight_percent, w.getWaterLevel_percent(), places=3)

    # TODO check these if the math is correct
    @data((0, 0.0), (25.0, 41666.6666), (50.0, 83333.3333), (100.0, 166666.6666))
    @unpack
    def test_water_emissionValve(self, opening, expectedFlow):
        w = Water(5.0, 60.0, 1000.0, 1000.0, 100.0)
        flow = w.emissionValve_percent_ToFlow_m3_per_s(opening)
        self.assertAlmostEqual(expectedFlow, flow, places=3)
