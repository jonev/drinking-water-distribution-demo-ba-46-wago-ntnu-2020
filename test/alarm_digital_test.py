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

    def test_acknowledge_while_alarm_is_high(self):
        instance = AlarmDigital(Timer(0.0, 0.0))
        self.assertFalse(instance.alarm)
        self.assertTrue(instance.acknowledge)
        instance.input(True)
        self.assertTrue(instance.alarm)
        self.assertFalse(instance.acknowledge)
        instance.acknowledgeCommand()
        self.assertTrue(instance.acknowledge)
        self.assertTrue(instance.alarm)

    def test_acknowledge_after_alarm_is_low_again(self):
        instance = AlarmDigital(Timer(0.0, 0.0))
        self.assertFalse(instance.alarm)
        self.assertTrue(instance.acknowledge)
        instance.input(True)
        self.assertTrue(instance.alarm)
        self.assertFalse(instance.acknowledge)
        instance.input(False)
        self.assertFalse(instance.alarm)
        self.assertFalse(instance.acknowledge)
        instance.acknowledgeCommand()
        self.assertTrue(instance.acknowledge)

    def test_acknowledge_on_two_alarms_two_acks(self):
        instance = AlarmDigital(Timer(0.0, 0.0))
        self.assertFalse(instance.alarm)
        self.assertTrue(instance.acknowledge)
        instance.input(True)
        self.assertTrue(instance.alarm)
        self.assertFalse(instance.acknowledge)
        instance.input(False)
        self.assertFalse(instance.alarm)
        self.assertFalse(instance.acknowledge)
        instance.acknowledgeCommand()
        self.assertTrue(instance.acknowledge)
        self.assertFalse(instance.alarm)
        self.assertTrue(instance.acknowledge)
        instance.input(True)
        self.assertTrue(instance.alarm)
        self.assertFalse(instance.acknowledge)
        instance.input(False)
        self.assertFalse(instance.alarm)
        self.assertFalse(instance.acknowledge)
        instance.acknowledgeCommand()
        self.assertTrue(instance.acknowledge)

    def test_acknowledge_on_two_alarms_one_ack(self):
        instance = AlarmDigital(Timer(0.0, 0.0))
        self.assertFalse(instance.alarm)
        self.assertTrue(instance.acknowledge)
        instance.input(True)
        self.assertTrue(instance.alarm)
        self.assertFalse(instance.acknowledge)
        instance.input(False)
        self.assertFalse(instance.alarm)
        self.assertFalse(instance.acknowledge)
        instance.input(True)
        self.assertTrue(instance.alarm)
        self.assertFalse(instance.acknowledge)
        instance.input(False)
        self.assertFalse(instance.alarm)
        self.assertFalse(instance.acknowledge)
        instance.acknowledgeCommand()
        self.assertTrue(instance.acknowledge)
