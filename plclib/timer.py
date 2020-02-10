import time


class Timer:
    """Standard timer with on and off delay
    
    :Version:
        1.0
    :Authors:
        Jone Vassbø
    """

    def __init__(self, onDelay, offDelay, tag=None):
        """Constructor method.
        
        :param onDelay: Number of seconds for on delay
        :type onDelay: Timer
        :param offDelay: Number of seconds for off delay
        :type offDelay: Timer
        """
        self.__id = tag
        self.__tag = tag
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

    # TODO write unit-tests
    def getBSON(self):
        """Converts this object to a BSON (mongodb compatable) object.
        
        :return: BSON object
        :rtype: BSON
        """
        return {
            "_id": self.__id,
            "tag": self.__tag,
            "onDelay": self.__onDelay,
            "offDelay": self.__offDelay,
            "onTime": self.__onTime,
            "offTime": self.__offTime,
        }

    # TODO write unit-tests
    @staticmethod
    def getTimer(bsonObject):
        """Converts a BSON object to a Timer object
        
        :param bsonObject: BSON object
        :type bsonObject: BSON
        :return: Timer object
        :rtype: Timer
        """
        t = Timer(bsonObject["onDelay"], bsonObject["offDelay"])
        t.__id = bsonObject["_id"]
        t.__tag = bsonObject["tag"]
        t.__inputSignalLastScan = False
        t.__onTime = bsonObject["onTime"]
        t.__offTime = bsonObject["offTime"]
        t.__inputSignal = False
        return t

