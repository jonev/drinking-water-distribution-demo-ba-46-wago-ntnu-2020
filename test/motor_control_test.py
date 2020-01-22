import unittest

from plclib.motor_control import MotorControl


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

    def test_interlock_isTrue(self):
        instance = MotorControl("testtag")
        instance.setAuto(True)
        instance.startCommandAuto()
        self.assertTrue(instance.controlValue)
        instance.interlock(True)
        self.assertTrue(instance.controlValue)

    def test_interlock_isFalse(self):
        instance = MotorControl("testtag")
        instance.setAuto(True)
        instance.startCommandAuto()
        self.assertTrue(instance.controlValue)
        instance.interlock(False)
        instance.startCommandAuto()
        self.assertFalse(instance.controlValue)

    def test_interlock_isFalseThenTrue(self):
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

