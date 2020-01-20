import time


class AlarmDigital:
    """Standard digital alarm
    """

    def __init__(self, alarmDelayOn, alarmDelayOff):
        self.__alarmDelayOn = alarmDelayOn
        self.__alarmDelayOff = alarmDelayOff
        self.__alarmSignal = False

    def input(self, *alarmSignals):
        self.__alarmSignal = False
        for alarmSignal in alarmSignals:
            if alarmSignal:
                if not self.__alarmSignal:
                    self.__alarmOnTime = time.time()
                self.__alarmSignal = True
                break

    @property
    def alarm(self):
        return self.__alarmSignal & ((self.__alarmDelayOn + self.__alarmDelayOn) < time.time())
