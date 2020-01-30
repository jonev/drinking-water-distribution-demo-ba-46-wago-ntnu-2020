import unittest

from plclib.analog_signal import AnalogSignal
from plclib.alarm_digital import AlarmDigital
from plclib.timer import Timer
from plclib.utils import Scaling


class AnalogSignalTest(unittest.TestCase):
    def test_simulation_mode(self):
        instance = AnalogSignal(tag="testtag")
        instance.rawInput(100.0)
        self.assertEqual(100.0, instance.output)
        instance.setSimulationValue(50.0)
        self.assertFalse(instance.simulationActive)
        instance.setSimulationMode(True)
        self.assertTrue(instance.simulationActive)
        self.assertEqual(50.0, instance.output)
        instance.setSimulationMode(False)
        self.assertFalse(instance.simulationActive)
        self.assertEqual(100.0, instance.output)

    def test_alarm_high(self):
        instance = AnalogSignal(tag="testtag", alarmHigh=AlarmDigital(Timer(0.0, 0.0)))
        instance.rawInput(49.0)
        instance.setAlarmHighLimit(50.0)
        self.assertFalse(instance.alarmHigh.alarm)
        instance.rawInput(50.0)
        self.assertTrue(instance.alarmHigh.alarm)
        instance.rawInput(49.0)
        self.assertFalse(instance.alarmHigh.alarm)

    def test_alarm_high_high(self):
        instance = AnalogSignal(tag="testtag", alarmHighHigh=AlarmDigital(Timer(0.0, 0.0)))
        instance.rawInput(49.0)
        instance.setAlarmHighHighLimit(50.0)
        self.assertFalse(instance.alarmHighHigh.alarm)
        instance.rawInput(50.0)
        self.assertTrue(instance.alarmHighHigh.alarm)
        instance.rawInput(49.0)
        self.assertFalse(instance.alarmHighHigh.alarm)

    def test_alarm_low(self):
        instance = AnalogSignal(tag="testtag", alarmLow=AlarmDigital(Timer(0.0, 0.0)))
        instance.rawInput(50.0)
        instance.setAlarmLowLimit(49.0)
        self.assertFalse(instance.alarmLow.alarm)
        instance.rawInput(49.0)
        self.assertTrue(instance.alarmLow.alarm)
        instance.rawInput(50.0)
        self.assertFalse(instance.alarmLow.alarm)

    def test_alarm_low_low(self):
        instance = AnalogSignal(tag="testtag", alarmLowLow=AlarmDigital(Timer(0.0, 0.0)))
        instance.rawInput(50.0)
        instance.setAlarmLowLowLimit(49.0)
        self.assertFalse(instance.alarmLowLow.alarm)
        instance.rawInput(49.0)
        self.assertTrue(instance.alarmLowLow.alarm)
        instance.rawInput(50.0)
        self.assertFalse(instance.alarmLowLow.alarm)

    def test_alarm_missing_exception(self):
        instance = AnalogSignal(tag="testtag")
        instance.rawInput(50.0)
        instance.setAlarmLowLowLimit(49.0)
        with self.assertRaises(AttributeError):
            instance.alarmLowLow.alarm

    def test_scaling(self):
        instance = AnalogSignal(tag="testtag", scaling=Scaling(0.0, 1.0, 100.0, 200.0))
        instance.rawInput(0.5)
        self.assertEqual(150.0, instance.output)

