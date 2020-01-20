class MotorControl:
    """Standard motor control block
    """

    def __init__(self, tag):
        self.__tag = tag
        self.__controlValueCommand = False
        self.__interlock = True

    def startCommand(self):
        """Start the motor
        """
        self.__controlValueCommand = True

    def stopCommand(self):
        """Stop the motor
        """
        self.__controlValueCommand = False

    def interlock(self, *interlocks):
        self.__interlock = True
        for interlock in interlocks:
            if not interlock:
                self.__interlock = False
                self.__controlValueCommand = False
                break

    @property
    def controlValue(self):
        return self.__controlValueCommand & self.__interlock

    @property
    def tag(self):
        return self.__tag
