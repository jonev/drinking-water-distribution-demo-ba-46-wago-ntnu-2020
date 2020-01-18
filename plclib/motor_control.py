
class MotorControl:
    def __init__(self, tag):
        self.__tag = tag
        self.__out = False

    def start(self):
        self.__out = True

    def stop(self):
        self.__out = False

    @property
    def out(self):
        return self.__out

    @property
    def tag(self):
        return self.__tag
