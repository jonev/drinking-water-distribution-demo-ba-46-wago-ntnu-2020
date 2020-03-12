import logging
import threading
import time

logging.basicConfig(filename="example.log", level=logging.DEBUG)


def dojob():
    logging.debug(str(time.time()))
    for x in range(1, 100000):
        # if x % 100000 == 0:
        #    print("Metod1: " + str(x))
        y = 2 + x ** 2 - x ** 10 - 15000
        z = y ** 15 - 15000 + (x - y)
    # print("Done")


def dojob2():
    print("Job 2")


class SimpleTaskScheduler:
    """ Simple task scheduler
        Schedules a task every chosen intervall (seconds)
        NB: If the task does not finish at all, the first time, there will not be raised an exception
    
    :raises Exception: Last task is not done when task is started
    """

    def __init__(self, task, runIntervalInSeconds, checkIntervalInSeconds):
        self.__runIntervalInSeconds = runIntervalInSeconds
        self.__checkIntervalInSeconds = checkIntervalInSeconds
        self.__runflag = True
        self.__task = task
        self.__starterThread = threading.Thread(target=self.__starterThreadMethod, args=())

    def start(self):
        self.__starttime = time.time()
        self.__starterThread.start()

    def join(self):
        self.__starterThread.join()
    
    def stop(self):
        self.__runflag = False

    def __starterThreadMethod(self):
        while self.__runflag:
            self.__starttime = self.__starttime + self.__intervallInSeconds
            worker = threading.Thread(target=self.__task, args=())
            worker.start()
            worker.join()
            if self.__starttime < time.time():
                raise Exception("Last task was not done -> increase the interval")
            while self.__starttime > time.time():
                time.sleep(self.__checkIntervalInSeconds)


s = SimpleTaskScheduler(dojob, 2.0, 0.1)
s.start()
s.join()
