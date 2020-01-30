import unittest
import time
from plclib.alarm_digital import AlarmDigital
from plclib.timer import Timer


class AlarmDigitalTest(unittest.TestCase):
    def test_alarm(self):
        instance = AlarmDigital(Timer(0.0, 0.0))
        self.assertFalse(instance.alarm)
        instance.input(True)
        self.assertTrue(instance.alarm)

    def test_alarm_onDelay(self):
        instance = AlarmDigital(Timer(1.0, 0.0))
        self.assertFalse(instance.alarm)
        instance.input(True)
        time.sleep(0.2)
        self.assertFalse(instance.alarm)
        time.sleep(0.9)
        self.assertTrue(instance.alarm)
        instance.input(False)
        self.assertFalse(instance.alarm)

    def test_alarm_offDelay(self):
        instance = AlarmDigital(Timer(0.0, 1.0))
        self.assertFalse(instance.alarm)
        instance.input(True)
        self.assertTrue(instance.alarm)
        instance.input(False)
        self.assertTrue(instance.alarm)
        time.sleep(0.5)
        self.assertTrue(instance.alarm)
        time.sleep(0.6)
        self.assertFalse(instance.alarm)

    def test_alarm_onDelay_and_offDelay(self):
        instance = AlarmDigital(Timer(0.5, 0.5))
        self.assertFalse(instance.alarm)
        instance.input(True)
        self.assertFalse(instance.alarm)
        time.sleep(0.5)
        self.assertTrue(instance.alarm)
        instance.input(False)
        self.assertTrue(instance.alarm)
        time.sleep(0.5)
        self.assertFalse(instance.alarm)

    def test_acknowledged_while_alarm_is_high(self):
        instance = AlarmDigital(Timer(0.0, 0.0))
        self.assertFalse(instance.alarm)
        self.assertTrue(instance.acknowledged)
        instance.input(True)
        self.assertTrue(instance.alarm)
        self.assertFalse(instance.acknowledged)
        instance.acknowledgeCommand()
        self.assertTrue(instance.acknowledged)
        self.assertTrue(instance.alarm)

    def test_acknowledged_after_alarm_is_low_again(self):
        instance = AlarmDigital(Timer(0.0, 0.0))
        self.assertFalse(instance.alarm)
        self.assertTrue(instance.acknowledged)
        instance.input(True)
        self.assertTrue(instance.alarm)
        self.assertFalse(instance.acknowledged)
        instance.input(False)
        self.assertFalse(instance.alarm)
        self.assertFalse(instance.acknowledged)
        instance.acknowledgeCommand()
        self.assertTrue(instance.acknowledged)

    def test_acknowledged_on_two_alarms_two_acks(self):
        instance = AlarmDigital(Timer(0.0, 0.0))
        self.assertFalse(instance.alarm)
        self.assertTrue(instance.acknowledged)
        instance.input(True)
        self.assertTrue(instance.alarm)
        self.assertFalse(instance.acknowledged)
        instance.input(False)
        self.assertFalse(instance.alarm)
        self.assertFalse(instance.acknowledged)
        instance.acknowledgeCommand()
        self.assertTrue(instance.acknowledged)
        self.assertFalse(instance.alarm)
        self.assertTrue(instance.acknowledged)
        instance.input(True)
        self.assertTrue(instance.alarm)
        self.assertFalse(instance.acknowledged)
        instance.input(False)
        self.assertFalse(instance.alarm)
        self.assertFalse(instance.acknowledged)
        instance.acknowledgeCommand()
        self.assertTrue(instance.acknowledged)

    def test_acknowledged_on_two_alarms_one_ack(self):
        instance = AlarmDigital(Timer(0.0, 0.0))
        self.assertFalse(instance.alarm)
        self.assertTrue(instance.acknowledged)
        instance.input(True)
        self.assertTrue(instance.alarm)
        self.assertFalse(instance.acknowledged)
        instance.input(False)
        self.assertFalse(instance.alarm)
        self.assertFalse(instance.acknowledged)
        instance.input(True)
        self.assertTrue(instance.alarm)
        self.assertFalse(instance.acknowledged)
        instance.input(False)
        self.assertFalse(instance.alarm)
        self.assertFalse(instance.acknowledged)
        instance.acknowledgeCommand()
        self.assertTrue(instance.acknowledged)
