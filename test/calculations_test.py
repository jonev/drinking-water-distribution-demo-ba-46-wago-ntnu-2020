import unittest
from ddt import ddt, data, unpack

from LeakDetection.divcalculations import DivCalculations


@ddt
class DivCalculationsTest(unittest.TestCase):
    @data(
        ([[1, 0], [2, 0], [3, 0], [4, 0], [5, 0]], 0, 3.0),
        ([[1, 0], [2, 0], [3, 0], [4, 0], [5, 0]], 1, 0),
        ([[3, 0], [3, 0], [3, 0], [4, 0], [4, 0], [4, 0]], 0, 3.5),
        ([[3, 0], [3, 0], [3, 0], [4, 0], [4, 0], [4, 0]], 1, 0),
    )
    @unpack
    def test_scale(self, samples, value_column_nr, result):
        self.assertEqual(result, DivCalculations.avgValue(samples, value_column_nr))
