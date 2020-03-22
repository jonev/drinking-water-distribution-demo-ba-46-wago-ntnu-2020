import logging
import threading
import time
from datetime import datetime


class SimpleTaskScheduler:
    """ Simple task scheduler
        Schedules a task every chosen intervall (seconds)
        NB: If the task does not finish at all, the first time, there will not be raised an exception
    
    :raises Exception: Last task is not done when task is started
    """

    def __init__(self, task, runIntervalInSeconds, delay, checkIntervalInSeconds):
        """Constructor
        The task will run on whole time periodes + delay.

        :param task: the task to be done
        :type task: method
        :param runIntervalInSeconds: How often the task will be executed in seconds
        :type runIntervalInSeconds: int
        :param delay: Delay after whole time period, in seconds
        :type delay: int
        :param checkIntervalInSeconds: How often the program should check if it should start the task (possible delay before the task executes), in seconds
        :type checkIntervalInSeconds: int
        """
        self.__runIntervalInSeconds = runIntervalInSeconds
        self.__delay = delay
        self.__checkIntervalInSeconds = checkIntervalInSeconds
        self.__runflag = True
        self.__task = task
        self.__starterThread = threading.Thread(target=self.__starterThreadMethod, args=())

    def start(self):
        """Start the scheduler
        """
        self.__starterThread.start()

    def join(self):
        """Join the scheduler task - Wait for the the scheduler to finish
        """
        self.__starterThread.join()

    def stop(self):
        """Stop the scheduler
        """
        self.__runflag = False

    def __starterThreadMethod(self):
        """Thread of the scheduler. Executes the task and insures that the interval is held.
        
        :raises Exception: Raises exception if the task is taking longer time than the intervall of the task
        """
        t = time.time()
        self.__starttime = (
            t - (t % self.__runIntervalInSeconds) + self.__runIntervalInSeconds + self.__delay
        )
        while self.__runflag:
            if self.__starttime < time.time():
                raise Exception("Last task was not done -> increase the interval")
            while self.__starttime > time.time():
                time.sleep(self.__checkIntervalInSeconds)
            worker = threading.Thread(
                target=self.__task, args=(datetime.fromtimestamp(self.__starttime),)
            )
            self.__starttime = self.__starttime + self.__runIntervalInSeconds
            worker.start()
            worker.join()
