class ValveAnalog:
    """Standard analog valve control
    Features:
    - Auto/manual
    - Transfer alarm
    """

    def __init__(self, tag):
        self.__tag = tag  # TODO

    def interlock(self, *interlocks):
        pass  # TODO

    def manualOpen(self):
        pass  # TODO

    @property
    def controlValue(self):
        return 0.0  # TODO

    @property
    def tag(self):
        return self.__tag
