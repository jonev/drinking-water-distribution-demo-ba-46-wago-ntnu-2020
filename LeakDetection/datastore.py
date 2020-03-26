import queue


class FtData:
    def __init__(self, _tagId):
        self._tagId = _tagId
        self.pointsOver10 = 0
        self.pointsOver20 = 0
        self.pointsOver30 = 0
        self.queuePointsOver10 = queue.Queue()
        self.queuePointsOver20 = queue.Queue()
        self.queuePointsOver30 = queue.Queue()
        for i in range(24):
            self.queuePointsOver10.put(0)
            self.queuePointsOver20.put(0)
            self.queuePointsOver30.put(0)
