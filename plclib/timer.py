import time


class Timer:
    """Standard timer
    """

    def __init__(self, onDelay, offDelay):
        self.__onDelay = onDelay
        self.__offDelay = offDelay
        self.__inputSignalLastScan = False
        self.__onTime = 0.0
        self.__offTime = 0.0
        self.__inputSignal = False

    def input(self, inputSignal):
        self.__inputSignal = inputSignal
        if inputSignal and not self.__inputSignalLastScan:
            self.__onTime = time.time()
        if not inputSignal and self.__inputSignalLastScan:
            self.__offTime = time.time()
        self.__inputSignalLastScan = inputSignal

    @property
    def output(self):
        return (self.__inputSignal and (self.__onTime + self.__onDelay) <= time.time()) or (
            not self.__inputSignal and (self.__offTime + self.__offDelay) > time.time()
        )
