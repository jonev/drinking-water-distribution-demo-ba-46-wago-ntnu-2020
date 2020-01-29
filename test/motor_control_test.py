import unittest

from plclib.motor_control import MotorControl
from plclib.alarm_digital import AlarmDigital
from plclib.timer import Timer


class MotorControlTest(unittest.TestCase):
    def test_auto_start(self):
        instance = MotorControl("testtag")
        instance.setAuto(True)
        self.assertFalse(instance.controlValue)
        instance.startCommandAuto()
        self.assertTrue(instance.controlValue)

    def test_auto_stop(self):
        instance = MotorControl("testtag")
        instance.setAuto(True)
        self.assertFalse(instance.controlValue)
        instance.startCommandAuto()
        self.assertTrue(instance.controlValue)
        instance.stopCommandAuto()
        self.assertFalse(instance.controlValue)

    def test_auto_interlock_isTrue(self):
        instance = MotorControl("testtag")
        instance.setAuto(True)
        instance.startCommandAuto()
        self.assertTrue(instance.controlValue)
        instance.interlock(True)
        self.assertTrue(instance.controlValue)

    def test_auto_interlock_isFalse(self):
        instance = MotorControl("testtag")
        instance.setAuto(True)
        instance.startCommandAuto()
        self.assertTrue(instance.controlValue)
        instance.interlock(False)
        instance.startCommandAuto()
        self.assertFalse(instance.controlValue)

    def test_auto_interlock_isFalseThenTrue(self):
        instance = MotorControl("testtag")
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
        instance = MotorControl("testtag")
        self.assertFalse(instance.controlValue)
        instance.startCommandManual()
        self.assertTrue(instance.controlValue)

    def test_manual_stop(self):
        instance = MotorControl("testtag")
        self.assertFalse(instance.controlValue)
        instance.startCommandManual()
        self.assertTrue(instance.controlValue)
        instance.stopCommandManual()
        self.assertFalse(instance.controlValue)

    def test_manual_interlock_isTrue(self):
        instance = MotorControl("testtag")
        instance.startCommandManual()
        self.assertTrue(instance.controlValue)
        instance.interlock(True)
        self.assertTrue(instance.controlValue)

    def test_manual_interlock_isFalse(self):
        instance = MotorControl("testtag")
        instance.startCommandManual()
        self.assertTrue(instance.controlValue)
        instance.interlock(False)
        instance.startCommandManual()
        self.assertFalse(instance.controlValue)

    def test_manual_interlock_isFalseThenTrue(self):
        instance = MotorControl("testtag")
        instance.startCommandManual()
        self.assertTrue(instance.controlValue)
        instance.interlock(False)
        self.assertFalse(instance.controlValue)
        instance.interlock(True)
        self.assertFalse(instance.controlValue)
        instance.startCommandManual()
        self.assertTrue(instance.controlValue)

    def test_manual_alarmStartFailed(self):
        instance = MotorControl(
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
        instance = MotorControl(tag="testtag", alarmDigitalStopFailed=AlarmDigital(Timer(0.0, 0.0)))
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
        instance = MotorControl(tag="testtag")
        with self.assertRaises(AttributeError):
            instance.alarmStartFailed.alarm
    def test_alarmStartFailed_exception_on_missing_AlarmDigital_instance(self):
        instance = MotorControl(tag="testtag")
        with self.assertRaises(AttributeError):
            instance.alarmStartFailed.alarm
