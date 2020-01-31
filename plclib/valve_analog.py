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

    def __init__(self, tag="no tag"):
        """Init with first run"""

        self.__tag = tag
        self.__auto = False
        self.__autoControlValueCommand = False
        self.__manualControlValueCommand = False

    def setAuto(self, value):
        self.__auto = value
        """Set the control mode to automatic - True, or manual - False.
        :param value: True or False, automatic or manual
        :type value: bool
        """

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
        self.__manuelControlValueCommand = True

    def closeCommandManual(self):
        """Close valve in manual mode
        """
        self.__manuelControlValueCommand = False

    @property
    def controlValue(self):
        # Du har jo ikke lagt til auto modus?
        return (self.__auto and self.__autoControlValueCommand) or (
            not self.__auto and self.__manualControlValueCommand
        )

    @property
    def tag(self):
        return self.__tag
