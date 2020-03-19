import logging
import threading
import time


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
        self.__starterThread.start()

    def join(self):
        self.__starterThread.join()

    def stop(self):
        self.__runflag = False

    def __starterThreadMethod(self):
        t = time.time()
        self.__starttime = t - (t % self.__runIntervalInSeconds) + self.__runIntervalInSeconds
        while self.__runflag:
            if self.__starttime < time.time():
                raise Exception("Last task was not done -> increase the interval")
            while self.__starttime > time.time():
                time.sleep(self.__checkIntervalInSeconds)
            self.__starttime = self.__starttime + self.__runIntervalInSeconds
            worker = threading.Thread(target=self.__task, args=())
            worker.start()
            worker.join()
