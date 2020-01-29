class AlarmDigital:
    """Standard digital alarm
    """

    def __init__(self, timer):
        self.__timer = timer
        self.__alarmSignal = False
        self.__acknowledge = True
        self.__acknowledgeCommand = False

    def input(self, alarmSignal):
        self.__alarmSignal = alarmSignal
        self.__timer.input(alarmSignal)

    def acknowledgeCommand(self):
        self.__acknowledge = True
        self.__acknowledgeCommand = True

    @property
    def alarm(self):
        return self.__timer.output

    @property
    def acknowledge(self):
        if self.alarm and not self.__acknowledgeCommand:
            self.__acknowledge = False
        if not self.alarm and self.__acknowledgeCommand:
            self.__acknowledgeCommand = False

        return self.__acknowledge
