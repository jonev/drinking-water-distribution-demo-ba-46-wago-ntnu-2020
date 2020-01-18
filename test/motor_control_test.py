import unittest

from plclib.motor_control import MotorControl

class MotorControlTest(unittest.TestCase):
    
    def test_start(self):
        instance = MotorControl("testtag")
        assert instance.out == False
        instance.start()
        assert instance.out == True

    def test_stop(self):
        instance = MotorControl("testtag")
        assert instance.out == False
        instance.start()
        assert instance.out == True
        instance.stop()
        assert instance.out == False