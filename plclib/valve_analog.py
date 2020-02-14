class ValveDigital:
    """
    Regner med han får info fra HMI om det skal kjøres i manuel eller auto. Dvs to variabler.
    Deretter en variabel til fra HMI som setter manuelåpning. Dvs en variabel
    Pluss en variabel som kommer fra programmet for og sett åpning på ventil ved auto
    Totatal 4 variabler inn i programmet

    Må sikkert på tilbakemelding på om den er i auto eller manuel. To variabler
    Og hvilken åpning ventilen står i. en variabel
    Total 3 variabler ut.

    Standard analog valve control
    Features:
    - Auto/manual
    - Transfer alarm
    In:
    Manual control value form HMI
    Auto control value from logic
    Manual and auto command from HMI
    Out:
    ControlValue
    """

    def __init__(self, tag="no tag", alarmDigitalOpenFailed=None, alarmDigitalCloseFailed=None):
        """Constructor method.
        
        :param tag: Tag name, defaults to "no tag"
        :type tag: str, optional
        :param alarmDigitalOpenFailed: Digital alarm for open failed, defaults to None
        :type alarmDigitalOpenFailed: AlarmDigital, optional
        :param alarmDigitalCloseFailed: Digital alarm for close failed, defaults to None
        :type alarmDigitalCloseFailed: AlarmDigital, optional
        """
        self.__tag = tag
        self.__auto = False
        self.__autoControlValueCommand = False
        self.__manualControlValueCommand = False
        self.__alarmDigitalOpenFailed = alarmDigitalOpenFailed
        self.__alarmDigitalCloseFailed = alarmDigitalCloseFailed
        self.__openedFeedback = False
        self.__closedFeedback = False

    def setAuto(self, value):
        """Set the control mode to automatic - True, or manual - False.
        :param value: True or False, automatic or manual
        :type value: bool
        """
        self.__auto = value

    def openCommandAuto(self):
        """Open valve in auto mode
        """
        self.__autoControlValueCommand = True

    def closeCommandAuto(self):
        """Close valve in auto mode
        """
        self.__autoControlValueCommand = False

    def openCommandManual(self):
        """Open valve in manual mode
        """
        self.__manualControlValueCommand = True

    def closeCommandManual(self):
        """Close valve in manual mode
        """
        self.__manualControlValueCommand = False

    def setOpenedFeedback(self, openedFeedback):
        """Digital feedback that the valve is opened. 
        Used to generate an alarm if it failes to open.
        
        :param openedFeedback: Feedback that the valve has opened
        :type openedFeedback: bool
        """
        self.__openedFeedback = openedFeedback

    def setClosedFeedback(self, closedFeedback):
        """Digital feedback that the valve is closed. 
        Used to generate an alarm if it failes to close.
        
        :param closedFeedback: Feedback that the valve has closed
        :type closedFeedback: bool
        """
        self.__closedFeedback = closedFeedback

    @property
    def controlValue(self):
        return (self.__auto and self.__autoControlValueCommand) or (
            not self.__auto and self.__manualControlValueCommand
        )

    @property
    def tag(self):
        return self.__tag

    @property
    def alarmOpenFailed(self):
        """Alarm; if the valve is asked to open, but the open feedback is false.
        
        :return: Alarm object
        :rtype: AlarmDigital
        """
        self.__alarmDigitalOpenFailed.input(not self.__openedFeedback and self.controlValue)
        return self.__alarmDigitalOpenFailed

    @property
    def alarmCloseFailed(self):
        """Alarm; if the valve is asked to close, but the close feedback is false.
        
        :return: Alarm object
        :rtype: AlarmDigital
        """
        self.__alarmDigitalCloseFailed.input(self.__closedFeedback and self.controlValue)
        return self.__alarmDigitalCloseFailed
