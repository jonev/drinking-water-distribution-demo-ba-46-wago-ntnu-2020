class ValveAnalog:
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

    def controlLogic(self):  # Bør klare oss uten en slik
        # Check for alarm etc
        pass

    def __init__(self, tag): "Dette settes bare ved første kjøring?"
        self.__tag = tag  "# TODO Hva gjør tag?
        self.__autoCommand = True "Starter allitid i auto"
        self.__manuelValue = 0 "Må være verdi som kommer fra HMI"
        self.__autoValue = 0 "Verdi som kommer fra logic"

    def interlock(self, *interlocks):"Usikker på dette"
        pass  # TODO

    def valveControl(self): "Set manuel or auto mode. Always start in automode"
        if self.__autoCommand == True:
            self.__manualCommand = False
        elif self.__autoCommand == False: 
            self.__manualCommand = True

    def manualControl(self):
        if self.__manualCommand == True and self.__autoCommand == False: "Sjekker om den står i manuell"
        self.__valveValue=self.__manuelValue

    def autoControl(self):
        if self.__autoCommand == True and self.__autoCommand == False: "Sjekker om den står i auto"
            self.__valveValue=self.__autoValue
    @property
    def controlValue(self):"Aner ikke hva dette gjør"
        return 0.0  # TODO

    @property
    def tag(self):"Aner ikke hva dette gjør"
        return self.__tag
