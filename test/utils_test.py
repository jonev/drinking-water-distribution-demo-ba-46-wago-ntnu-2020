import unittest
from ddt import ddt, data, unpack

from plclib.utils import Scaling


@ddt
class UtilsTest(unittest.TestCase):
    @data(
        (100.0, 0.0, 1.0, 0.0, 100.0, 1.0),
        (50.0, 0.0, 1.0, 0.0, 100.0, 0.5),
        (100.0, 0.0, -1.0, 0.0, 100.0, -1.0),
        (50.0, 0.0, -1.0, 0.0, 100.0, -0.5),
        (-100.0, 0.0, 1.0, 0.0, -100.0, 1.0),
        (-50.0, 0.0, 1.0, 0.0, -100.0, 0.5),
        (150.0, 10.0, 15.0, 100.0, 200.0, 12.5),
        (150.0, 15.0, 10.0, 100.0, 200.0, 12.5),
    )
    @unpack
    def test_scale(self, expected, inMin, inMax, outMin, outMax, input):
        s = Scaling(inMin, inMax, outMin, outMax)
        self.assertEqual(expected, s.scale(input))
