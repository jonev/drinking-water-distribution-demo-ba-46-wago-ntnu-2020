import time


class Timer:
    """Standard timer with on and off delay
    
    :Version:
        1.0
    :Authors:
        Jone Vassbø
    """

    def __init__(self, onDelay, offDelay):
        """Constructor method.
        
        :param onDelay: Number of seconds for on delay
        :type onDelay: Timer
        :param offDelay: Number of seconds for off delay
        :type offDelay: Timer
        """
        self.__onDelay = onDelay
        self.__offDelay = offDelay
        self.__inputSignalLastScan = False
        self.__onTime = 0.0
        self.__offTime = 0.0
        self.__inputSignal = False

    def input(self, inputSignal):
        """Set the inputsignal of the timer.
        
        :param inputSignal: The signal to delay
        :type inputSignal: bool
        """
        self.__inputSignal = inputSignal
        if inputSignal and not self.__inputSignalLastScan:
            self.__onTime = time.time()
        if not inputSignal and self.__inputSignalLastScan:
            self.__offTime = time.time()
        self.__inputSignalLastScan = inputSignal

    @property
    def output(self):
        """Output signal which is delayed.
        
        :return: Delayed signal
        :rtype: bool
        """
        return (self.__inputSignal and (self.__onTime + self.__onDelay) <= time.time()) or (
            not self.__inputSignal and (self.__offTime + self.__offDelay) > time.time()
        )
