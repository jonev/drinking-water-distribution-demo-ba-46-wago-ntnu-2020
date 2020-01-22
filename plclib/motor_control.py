class MotorControl:
    """Standard motor control block
    """

    def __init__(self, tag):
        self.__tag = tag
        self.__autoControlValueCommand = False
        self.__interlock = True
        self.__auto = False

    def setAuto(self, value):
        self.__auto = value

    def startCommandAuto(self):
        """Start the motor in auto
        """
        self.__autoControlValueCommand = True

    def stopCommandAuto(self):
        """Stop the motor in auto
        """
        self.__autoControlValueCommand = False

    def interlock(self, interlock):
        self.__interlock = interlock
        if not interlock:
            self.__autoControlValueCommand = False

    @property
    def controlValue(self):
        return (self.__auto and self.__autoControlValueCommand) and self.__interlock

    @property
    def tag(self):
        return self.__tag
