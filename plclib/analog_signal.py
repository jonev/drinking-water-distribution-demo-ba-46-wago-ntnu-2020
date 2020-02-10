import json
from plclib.alarm_digital import AlarmDigital
from plclib.utils import Scaling


class AnalogSignal:
    """Standard block for analog signal, possibilities for alarms, simulation and scaling.

    :Version:
        1.0
    :Authors:
        Jone Vassbø
    """

    def __init__(
        self,
        tag="no tag",
        alarmHigh=None,
        alarmHighHigh=None,
        alarmLow=None,
        alarmLowLow=None,
        scaling=None,
    ):
        self.__id = tag
        self.__tag = tag
        self.__alarmHigh = alarmHigh
        self.__alarmHighHigh = alarmHighHigh
        self.__alarmLow = alarmLow
        self.__alarmLowLow = alarmLowLow
        self.__simulation = False
        self.__output = 0.0
        self.__simulationValue = 0.0
        self.__alarmHighLimit = 0.0
        self.__alarmHighHighLimit = 0.0
        self.__alarmLowLimit = 0.0
        self.__alarmLowLowLimit = 0.0
        self.__rawInput = 0.0
        self.__scaling = scaling

    def rawInput(self, value):
        """Raw input signal
        
        :param value: Raw input signal
        :type value: float
        """
        self.__rawInput = value

    def setSimulationMode(self, value):
        """Enable simulation.
        
        :param value: True or False, simulation active or not
        :type value: bool
        """
        self.__simulation = value

    def setSimulationValue(self, value):
        """Set value to be fed to output.
        
        :param value: Analog value to output
        :type value: bool
        """
        self.__simulationValue = value

    def setAlarmHighLimit(self, limit):
        self.__alarmHighLimit = limit

    def setAlarmHighHighLimit(self, limit):
        self.__alarmHighHighLimit = limit

    def setAlarmLowLimit(self, limit):
        self.__alarmLowLimit = limit

    def setAlarmLowLowLimit(self, limit):
        self.__alarmLowLowLimit = limit

    @property
    def simulationActive(self):
        return self.__simulation

    @property
    def output(self):
        """Output of analog signal, simulated, scaled or raw.
        
        :return: Analog output signal
        :rtype: float
        """
        if self.__simulation:
            return self.__simulationValue

        if self.__scaling is not None:
            return self.__scaling.scale(self.__rawInput)

        return self.__rawInput

    @property
    def alarmHigh(self):
        self.__alarmHigh.input(self.output >= self.__alarmHighLimit)
        return self.__alarmHigh

    @property
    def alarmHighHigh(self):
        self.__alarmHighHigh.input(self.output >= self.__alarmHighHighLimit)
        return self.__alarmHighHigh

    @property
    def alarmLow(self):
        self.__alarmLow.input(self.output <= self.__alarmLowLimit)
        return self.__alarmLow

    @property
    def alarmLowLow(self):
        self.__alarmLowLow.input(self.output <= self.__alarmLowLowLimit)
        return self.__alarmLowLow

    @property
    def tag(self):
        """Tag name of the signal.
        
        :return: The tag name
        :rtype: str
        """
        return self.__tag

    # TODO write unit-tests
    def getBSON(self):
        return {
            "_id": self.__tag,
            "type": AnalogSignal.__class__,
            "tag": self.__tag,
            "alarmHigh": self.__alarmHigh.getBSON() if self.__alarmHigh is not None else None,
            "alarmHighHigh": self.__alarmHighHigh.getBSON()
            if self.__alarmHighHigh is not None
            else None,
            "alarmLow": self.__alarmLow.getBSON() if self.__alarmLow is not None else None,
            "alarmLowLow": self.__alarmLowLow.getBSON() if self.__alarmLowLow is not None else None,
            "simulation": self.__simulation,
            "output": self.__output,
            "simulationValue": self.__simulationValue,
            "alarmHighLimit": self.__alarmHighLimit,
            "alarmHighHighLimit": self.__alarmHighHighLimit,
            "alarmLowLimit": self.__alarmLowLimit,
            "alarmLowLowLimit": self.__alarmLowLowLimit,
            "rawInput": self.__rawInput,
            "scaling": self.__scaling.getBSON() if self.__scaling is not None else None,
        }

    # TODO write unit-tests
    @staticmethod
    def getAnalogSignal(bsonObject):
        ah = (
            AlarmDigital.getAlarmDigital(bsonObject["alarmHigh"])
            if bsonObject["alarmHigh"] is not None
            else None
        )
        ahh = (
            AlarmDigital.getAlarmDigital(bsonObject["alarmHighHigh"])
            if bsonObject["alarmHighHigh"] is not None
            else None
        )
        al = (
            AlarmDigital.getAlarmDigital(bsonObject["alarmLow"])
            if bsonObject["alarmLow"] is not None
            else None
        )
        all = (
            AlarmDigital.getAlarmDigital(bsonObject["alarmLowLow"])
            if bsonObject["alarmLowLow"] is not None
            else None
        )
        sc = (
            Scaling.getScaling(bsonObject["scaling"]) if bsonObject["scaling"] is not None else None
        )

        a = AnalogSignal(
            tag=bsonObject["tag"],
            alarmHigh=ah,
            alarmHighHigh=ahh,
            alarmLow=al,
            alarmLowLow=all,
            scaling=sc,
        )
        a.__simulation = bsonObject["simulation"]
        a.__output = bsonObject["__output"]
        a.__simulationValue = bsonObject["simulationValue"]
        a.__alarmHighLimit = bsonObject["alarmHighLimit"]
        a.__alarmHighHighLimit = bsonObject["alarmHighHighLimit"]
        a.__alarmLowLimit = bsonObject["alarmLowLimit"]
        a.__alarmLowLowLimit = bsonObject["alarmLowLowLimit"]
        a.__rawInput = bsonObject["rawInput"]
        return a
