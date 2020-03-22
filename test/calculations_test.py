import unittest
from ddt import ddt, data, unpack

from LeakDetection.calculations import Calculations


@ddt
class CalculationsTest(unittest.TestCase):
    @data(
        ([[1, 0], [2, 0], [3, 0], [4, 0], [5, 0]], 0, 3.0),
        ([[1, 0], [2, 0], [3, 0], [4, 0], [5, 0]], 1, 0),
        ([[3, 0], [3, 0], [3, 0], [4, 0], [4, 0], [4, 0]], 0, 3.5),
        ([[3, 0], [3, 0], [3, 0], [4, 0], [4, 0], [4, 0]], 1, 0),
    )
    @unpack
    def test_scale(self, samples, value_column_nr, result):
        self.assertEqual(result, Calculations.avgValue(samples, value_column_nr))
