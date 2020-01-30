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

