import unittest

from plclib.motor_control import MotorControl


class MotorControlTest(unittest.TestCase):
    def test_start(self):
        instance = MotorControl("testtag")
        self.assertFalse(instance.controlValue)
        instance.start()
        self.assertTrue(instance.controlValue)

    def test_stop(self):
        instance = MotorControl("testtag")
        self.assertFalse(instance.controlValue)
        instance.start()
        self.assertTrue(instance.controlValue)
        instance.stop()
        self.assertFalse(instance.controlValue)

    def test_interlock_isTrue(self):
        instance = MotorControl("testtag")
        instance.start()
        self.assertTrue(instance.controlValue)
        instance.interlock(True, True, True)
        self.assertTrue(instance.controlValue)

    def test_interlock_isFalse(self):
        instance = MotorControl("testtag")
        instance.start()
        self.assertTrue(instance.controlValue)
        instance.interlock(True, False, True)
        instance.start()
        self.assertFalse(instance.controlValue)

    def test_interlock_isFalseThenTrue(self):
        instance = MotorControl("testtag")
        instance.start()
        self.assertTrue(instance.controlValue)
        instance.interlock(True, False, True)
        self.assertFalse(instance.controlValue)
        instance.interlock(True, True, True)
        self.assertFalse(instance.controlValue)
        instance.start()
        self.assertTrue(instance.controlValue)

