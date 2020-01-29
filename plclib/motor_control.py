class MotorControl:
    """Standard motor control block
    """

    def __init__(self, tag="no tag", alarmDigitalStartFailed=None, alarmDigitalStopFailed=None):
        self.__tag = tag
        self.__autoControlValueCommand = False
        self.__manualControlValueCommand = False
        self.__interlock = True
        self.__auto = False
        self.__alarmDigitalStartFailed = alarmDigitalStartFailed
        self.__alarmDigitalStopFailed = alarmDigitalStopFailed
        self.__startedFeedback = False
        self.__stoppedFeedback = False

    def setTag(self, tag):
        """Set the motors tag
        """
        self.__tag = tag

    def setAuto(self, value):
        """Set controlmode to automatic
        """
        self.__auto = value

    def startCommandAuto(self):
        """Start the motor in automatic mode
        """
        self.__autoControlValueCommand = True

    def stopCommandAuto(self):
        """Stop the motor in automatic mode
        """
        self.__autoControlValueCommand = False

    def startCommandManual(self):
        """Start the motor in manual
        """
        self.__manualControlValueCommand = True

    def stopCommandManual(self):
        """Stop the motor in manual
        """
        self.__manualControlValueCommand = False

    def interlock(self, interlock):
        """Interlock to prevent the motor from running. 
        Interlock needs to be True for the motor to be allowed to run.
        If the interlock stoppeds the motor, a new start command have to occur befor it starts.
        """
        self.__interlock = interlock
        if not interlock:
            self.__autoControlValueCommand = False
            self.__manualControlValueCommand = False

    def setStartedFeedback(self, startedFeedback):
        """Digital feedback that the motor is started. 
        Used to generate an alarm if it failes to start.
        """
        self.__startedFeedback = startedFeedback

    def setStoppedFeedback(self, stoppedFeedback):
        """Digital feedback that the motor is stopped. 
        Used to generate an alarm if it failes to stop.
        """
        self.__stoppedFeedback = stoppedFeedback

    @property
    def controlValue(self):
        """Control value to start the motor.
        """
        return (
            (not self.__auto and self.__manualControlValueCommand)
            or (self.__auto and self.__autoControlValueCommand)
        ) and self.__interlock

    @property
    def tag(self):
        return self.__tag

    @property
    def alarmStartFailed(self):
        """Alarm; if the motor is asked to start, but the start feedback is false.
        """
        self.__alarmDigitalStartFailed.input(not self.__startedFeedback and self.controlValue)
        return self.__alarmDigitalStartFailed

    @property
    def alarmStopFailed(self):
        """Alarm; if the motor is asked to stop, but the stop feedback is false.
        """
        self.__alarmDigitalStopFailed.input(self.__stoppedFeedback and self.controlValue)
        return self.__alarmDigitalStopFailed
