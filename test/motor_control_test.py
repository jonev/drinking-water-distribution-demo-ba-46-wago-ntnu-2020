import unittest

from plclib.motor_control import MotorControlDigitalDigital
from plclib.alarm_digital import AlarmDigital
from plclib.timer import Timer


class MotorControlDigitalTest(unittest.TestCase):
    def test_auto_start(self):
        instance = MotorControlDigitalDigital("testtag")
        instance.setAuto(True)
        self.assertFalse(instance.controlValue)
        instance.startCommandAuto()
        self.assertTrue(instance.controlValue)

    def test_auto_stop(self):
        instance = MotorControlDigital("testtag")
        instance.setAuto(True)
        self.assertFalse(instance.controlValue)
        instance.startCommandAuto()
        self.assertTrue(instance.controlValue)
        instance.stopCommandAuto()
        self.assertFalse(instance.controlValue)

    def test_auto_interlock_isTrue(self):
        instance = MotorControlDigital("testtag")
        instance.setAuto(True)
        instance.startCommandAuto()
        self.assertTrue(instance.controlValue)
        instance.interlock(True)
        self.assertTrue(instance.controlValue)

    def test_auto_interlock_isFalse(self):
        instance = MotorControlDigital("testtag")
        instance.setAuto(True)
        instance.startCommandAuto()
        self.assertTrue(instance.controlValue)
        instance.interlock(False)
        instance.startCommandAuto()
        self.assertFalse(instance.controlValue)

    def test_auto_interlock_isFalseThenTrue(self):
        instance = MotorControlDigital("testtag")
        instance.setAuto(True)
        instance.startCommandAuto()
        self.assertTrue(instance.controlValue)
        instance.interlock(False)
        self.assertFalse(instance.controlValue)
        instance.interlock(True)
        self.assertFalse(instance.controlValue)
        instance.startCommandAuto()
        self.assertTrue(instance.controlValue)

    def test_manual_start(self):
        instance = MotorControlDigital("testtag")
        self.assertFalse(instance.controlValue)
        instance.startCommandManual()
        self.assertTrue(instance.controlValue)

    def test_manual_stop(self):
        instance = MotorControlDigital("testtag")
        self.assertFalse(instance.controlValue)
        instance.startCommandManual()
        self.assertTrue(instance.controlValue)
        instance.stopCommandManual()
        self.assertFalse(instance.controlValue)

    def test_manual_interlock_isTrue(self):
        instance = MotorControlDigital("testtag")
        instance.startCommandManual()
        self.assertTrue(instance.controlValue)
        instance.interlock(True)
        self.assertTrue(instance.controlValue)

    def test_manual_interlock_isFalse(self):
        instance = MotorControlDigital("testtag")
        instance.startCommandManual()
        self.assertTrue(instance.controlValue)
        instance.interlock(False)
        instance.startCommandManual()
        self.assertFalse(instance.controlValue)

    def test_manual_interlock_isFalseThenTrue(self):
        instance = MotorControlDigital("testtag")
        instance.startCommandManual()
        self.assertTrue(instance.controlValue)
        instance.interlock(False)
        self.assertFalse(instance.controlValue)
        instance.interlock(True)
        self.assertFalse(instance.controlValue)
        instance.startCommandManual()
        self.assertTrue(instance.controlValue)

    def test_manual_alarmStartFailed(self):
        instance = MotorControlDigital(
            tag="testtag", alarmDigitalStartFailed=AlarmDigital(Timer(0.0, 0.0))
        )
        self.assertFalse(instance.controlValue)
        self.assertFalse(instance.alarmStartFailed.alarm)
        instance.startCommandManual()
        instance.setStartedFeedback(True)
        self.assertFalse(instance.alarmStartFailed.alarm)
        instance.setStartedFeedback(False)
        self.assertTrue(instance.alarmStartFailed.alarm)
        instance.setStartedFeedback(True)
        self.assertFalse(instance.alarmStartFailed.alarm)

    def test_manual_alarmStoppedFailed(self):
        instance = MotorControlDigital(
            tag="testtag", alarmDigitalStopFailed=AlarmDigital(Timer(0.0, 0.0))
        )
        instance.setStoppedFeedback(True)
        self.assertFalse(instance.controlValue)
        self.assertFalse(instance.alarmStopFailed.alarm)
        instance.startCommandManual()
        instance.setStoppedFeedback(False)
        self.assertFalse(instance.alarmStopFailed.alarm)
        instance.setStoppedFeedback(True)
        self.assertTrue(instance.alarmStopFailed.alarm)
        instance.setStoppedFeedback(False)
        self.assertFalse(instance.alarmStopFailed.alarm)

    def test_alarmStoppedFailed_exception_on_missing_AlarmDigital_instance(self):
        instance = MotorControlDigital(tag="testtag")
        with self.assertRaises(AttributeError):
            instance.alarmStartFailed.alarm

    def test_alarmStartFailed_exception_on_missing_AlarmDigital_instance(self):
        instance = MotorControlDigital(tag="testtag")
        with self.assertRaises(AttributeError):
            instance.alarmStartFailed.alarm
