import json
from plclib.timer import Timer


class AlarmDigital:
    """Standard digital alarm

    :Version:
        1.0
    :Authors:
        Jone Vassbø
    """

    def __init__(self, timer, tag=None):
        """Constructor methond.
        
        :param timer: Timer to delay the alarm
        :type timer: Timer
        """
        self.__id = tag
        self.__tag = tag
        self.__timer = timer
        self.__alarmSignal = False
        self.__acknowledge = True
        self.__acknowledgeCommand = False

    def input(self, alarmSignal):
        """Input which triggers the alarm.
        
        :param alarmSignal: Input which triggers the alarm
        :type alarmSignal: bool
        """
        self.__alarmSignal = alarmSignal
        self.__timer.input(alarmSignal)

    def acknowledgeCommand(self):
        """Alarm is acknowledge command
        """
        self.__acknowledge = True
        self.__acknowledgeCommand = True

    @property
    def alarm(self):
        """Alarm signal
        
        :return: The alarm signal
        :rtype: bool
        """
        return self.__timer.output

    @property
    def acknowledged(self):
        """Alarm is acknowledged
        
        :return: The acknowledged signal
        :rtype: bool
        """
        if self.alarm and not self.__acknowledgeCommand:
            self.__acknowledge = False
        if not self.alarm and self.__acknowledgeCommand:
            self.__acknowledgeCommand = False

        return self.__acknowledge

    # TODO write unit-tests
    def getBSON(self):
        return {
            "_id": self.__id,
            "tag": self.__tag,
            "timer": self.__timer.getBSON(),
            "alarmSignal": self.__alarmSignal,
            "acknowledge": self.__acknowledge,
            "acknowledgeCommand": self.__acknowledgeCommand,
        }

    # TODO write unit-tests
    @staticmethod
    def getAlarmDigital(bsonObject):
        a = AlarmDigital(Timer.getTimer(bsonObject["timer"]))
        a.__id = bsonObject["_id"]
        a.__tag = bsonObject["tag"]
        a.__alarmSignal = bsonObject["alarmSignal"]
        a.__acknowledge = bsonObject["acknowledge"]
        a.__acknowledgeCommand = bsonObject["acknowledgeCommand"]
        return a
