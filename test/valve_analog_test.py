import unittest

from plclib.valve_analog import ValveDigital
from plclib.alarm_digital import AlarmDigital
from plclib.timer import Timer

# Sjekking av feil skjer når du lagrer filen, selv om det ikek er gjort endringer på den


class ValveDigitalTest(unittest.TestCase):
    def test_auto_open(self):
        instance = ValveDigital("testtag")
        # Kjorer ValveDigital med testtag som navn
        instance.setAuto(True)
        # Kjører def setAuto som setter self.__auto true."
        self.assertFalse(instance.controlValue)
        # Sjekker om at contolvalue er False. Ja for bare self._auto er aktiver og ikke self.__autoControlValueCommand
        instance.openCommandAuto()
        # kjører openCommandAuto som setter self.__autoControlValueCommand true
        self.assertTrue(instance.controlValue)
        # Sjekker nå om controlValue er true. ja, for begge betingelsene er oppfylt.
        # instance.closeCommandAuto() "Kjører closeCommandAuto som gjør at self.__autoControlValueCommand blir false
        # self.assertFalse(instance.controlValue) "Sjekker om controlValue er false,noe som den er siden forrige linje fjernet en betingelse

    def test_auto_close(self):
        instance = ValveDigital("testtag")
        instance.setAuto(True)
        self.assertFalse(instance.controlValue)
        instance.openCommandAuto()
        self.assertTrue(instance.controlValue)
        instance.closeCommandAuto()
        self.assertFalse(instance.controlValue)

    def test_manual_open(self):
        instance = ValveDigital("testtag")
        self.assertFalse(instance.controlValue)
        instance.openCommandManual()
        self.assertTrue(instance.controlValue)

    def test_manual_close(self):
        instance = ValveDigital("testtag")
        self.assertFalse(instance.controlValue)
        instance.openCommandManual()
        self.assertTrue(instance.controlValue)
        instance.closeCommandManual()
        self.assertFalse(instance.controlValue)

    def test_manual_alarmOpenFailed(self):
        instance = ValveDigital(tag="testtag", alarmDigitalOpenFailed=AlarmDigital(Timer(0.0, 0.0)))
        self.assertFalse(instance.controlValue)
        self.assertFalse(instance.alarmOpenFailed.alarm)
        instance.openCommandManual()
        instance.setOpenedFeedback(True)
        self.assertFalse(instance.alarmOpenFailed.alarm)
        instance.setOpenedFeedback(False)
        self.assertTrue(instance.alarmOpenFailed.alarm)
        instance.setOpenedFeedback(True)
        self.assertFalse(instance.alarmOpenFailed.alarm)

    def test_manual_alarmOpenedFailed(self):
        instance = ValveDigital(
            tag="testtag", alarmDigitalCloseFailed=AlarmDigital(Timer(0.0, 0.0))
        )
        instance.setClosedFeedback(True)
        self.assertFalse(instance.controlValue)
        self.assertFalse(instance.alarmCloseFailed.alarm)
        instance.openCommandManual()
        instance.setClosedFeedback(False)
        self.assertFalse(instance.alarmCloseFailed.alarm)
        instance.setClosedFeedback(True)
        self.assertTrue(instance.alarmCloseFailed.alarm)
        instance.setClosedFeedback(False)
        self.assertFalse(instance.alarmCloseFailed.alarm)

    def test_alarmClosedFailed_exception_on_missing_AlarmDigital_instance(self):  # Stopped
        instance = ValveDigital(tag="testtag")
        with self.assertRaises(AttributeError):
            instance.alarmOpenFailed.alarm  # Riktig med Open på begge disse ?

    def test_alarmOpenedFailed_exception_on_missing_AlarmDigital_instance(self):  # Start
        instance = ValveDigital(tag="testtag")
        with self.assertRaises(AttributeError):
            instance.alarmOpenFailed.alarm  # Riktig med Open på begge disse ?

