import unittest
import time
from plclib.alarm_digital import AlarmDigital


class AlarmDigitalTest(unittest.TestCase):
    def test_alarm(self):
        a = AlarmDigital(0.0, 0.0)
        self.assertFalse(a.alarm)
        a.input(False, True, False)
        self.assertTrue(a.alarm)

