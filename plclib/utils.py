class Scaling:
    """Standard scaling
    Source: https://math.stackexchange.com/questions/43698/range-scaling-problem

    :Version:
        1.0
    :Authors:
        Jone Vassbø
    """

    def __init__(self, inMin, inMax, outMin, outMax):
        """Constructor method
        
        :param inMin: input minimum value
        :type inMin: float
        :param inMax: input maximum value
        :type inMax: float
        :param outMin: output minimum value
        :type outMin: float
        :param outMax: output maximum value
        :type outMax: float
        """
        self.__inMin = inMin
        self.__inMax = inMax
        self.__outMin = outMin
        self.__outMax = outMax

    def scale(self, input):
        """ Scale input

        :param input: input value
        :type input: float
        :return: scaled value
        :rtype: float
        """
        return self.__outMin * (
            1 - ((input - self.__inMin) / (self.__inMax - self.__inMin))
        ) + self.__outMax * ((input - self.__inMin) / (self.__inMax - self.__inMin))

