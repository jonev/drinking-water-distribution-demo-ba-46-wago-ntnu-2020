from plclib.alarm_digital import AlarmDigital


class MotorControlDigital:
    """Standard control of a motor.

    :Version:
        1.0
    :Authors:
        Jone Vassbø
    """

    def __init__(self, tag="no tag", alarmDigitalStartFailed=None, alarmDigitalStopFailed=None):
        """Constructor method.
        
        :param tag: Tag name, defaults to "no tag"
        :type tag: str, optional
        :param alarmDigitalStartFailed: Digital alarm for start failed, defaults to None
        :type alarmDigitalStartFailed: AlarmDigital, optional
        :param alarmDigitalStopFailed: Digital alarm for stop failed, defaults to None
        :type alarmDigitalStopFailed: AlarmDigital, optional
        """
        self.__tag = tag
        self.__autoControlValueCommand = False
        self.__manualControlValueCommand = False
        self.__interlock = True
        self.__auto = False
        self.__alarmDigitalStartFailed = alarmDigitalStartFailed
        self.__alarmDigitalStopFailed = alarmDigitalStopFailed
        self.__startedFeedback = False
        self.__stoppedFeedback = False

    def setAuto(self, value):
        """Set the control mode to automatic - True, or manual - False.
        
        :param value: True or False, automatic or manual
        :type value: bool
        """
        self.__auto = value

    def startCommandAuto(self):
        """Start command in automatic mode.
        """
        self.__autoControlValueCommand = True

    def stopCommandAuto(self):
        """Stop the motor in automatic mode.
        """
        self.__autoControlValueCommand = False

    def startCommandManual(self):
        """Start the motor in manual mode.
        """
        self.__manualControlValueCommand = True

    def stopCommandManual(self):
        """Stop the motor in manual mode.
        """
        self.__manualControlValueCommand = False

    def interlock(self, interlock):
        """Interlock to prevent the motor from running. 
        Interlock needs to be True for the motor to be allowed to run.
        If the interlock stoppeds the motor, a new start command have to occur before it starts.
        
        :param interlock: True - motor can be started, False - motor is stopped
        :type interlock: bool
        """
        self.__interlock = interlock
        if not interlock:
            self.__autoControlValueCommand = False
            self.__manualControlValueCommand = False

    def setStartedFeedback(self, startedFeedback):
        """Digital feedback that the motor is started. 
        Used to generate an alarm if it failes to start.
        
        :param startedFeedback: Feedback that the motor has started
        :type startedFeedback: bool
        """
        self.__startedFeedback = startedFeedback

    def setStoppedFeedback(self, stoppedFeedback):
        """Digital feedback that the motor is stopped. 
        Used to generate an alarm if it failes to stop.
        
        :param stoppedFeedback: Feedback that the motor has stopped
        :type stoppedFeedback: bool
        """
        self.__stoppedFeedback = stoppedFeedback

    @property
    def controlValue(self):
        """Control value to start the motor.
        E.g. to control a digital output which starts the motor.
        """
        return (
            (not self.__auto and self.__manualControlValueCommand)
            or (self.__auto and self.__autoControlValueCommand)
        ) and self.__interlock

    @property
    def tag(self):
        """Tag name of the motor
        
        :return: The tag name
        :rtype: str
        """
        return self.__tag

    @property
    def alarmStartFailed(self):
        """Alarm; if the motor is asked to start, but the start feedback is false.
        
        :return: Alarm object
        :rtype: AlarmDigital
        """
        self.__alarmDigitalStartFailed.input(not self.__startedFeedback and self.controlValue)
        return self.__alarmDigitalStartFailed

    @property
    def alarmStopFailed(self):
        """Alarm; if the motor is asked to stop, but the stop feedback is false.
        
        :return: Alarm object
        :rtype: AlarmDigital
        """
        self.__alarmDigitalStopFailed.input(self.__stoppedFeedback and self.controlValue)
        return self.__alarmDigitalStopFailed

    # TODO write unit-tests
    def getBSON(self):
        return {
            "_id": self.__tag,
            "type": MotorControlDigital.__class__,
            "tag": self.__tag,
            "autoControlValueCommand": self.__autoControlValueCommand,
            "manualControlValueCommand": self.__manualControlValueCommand,
            "interlock": self.__interlock,
            "auto": self.__auto,
            "alarmDigitalStartFailed": self.__alarmDigitalStartFailed.getBSON()
            if self.__alarmDigitalStartFailed is not None
            else None,
            "alarmDigitalStopFailed": self.__alarmDigitalStopFailed.getBSON()
            if self.__alarmDigitalStopFailed is not None
            else None,
            "startedFeedback": self.__startedFeedback,
            "stoppedFeedback": self.__stoppedFeedback,
        }

    # TODO write unit-tests
    @staticmethod
    def getMotorControlDigital(bsonObject):
        aStart = (
            AlarmDigital.getAlarmDigital(bsonObject["alarmDigitalStartFailed"])
            if bsonObject["alarmDigitalStartFailed"] is not None
            else None
        )
        aStop = (
            AlarmDigital.getAlarmDigital(bsonObject["alarmDigitalStopFailed"])
            if bsonObject["alarmDigitalStopFailed"] is not None
            else None
        )
        m = MotorControlDigital(
            tag=bsonObject["tag"], alarmDigitalStartFailed=aStart, alarmDigitalStopFailed=aStop,
        )
        m.__autoControlValueCommand = bsonObject["autoControlValueCommand"]
        m.__manualControlValueCommand = bsonObject["manualControlValueCommand"]
        m.__interlock = bsonObject["interlock"]
        m.__auto = bsonObject["auto"]
        m.__startedFeedback = bsonObject["startedFeedback"]
        m.__stoppedFeedback = bsonObject["stoppedFeedback"]
        return m
