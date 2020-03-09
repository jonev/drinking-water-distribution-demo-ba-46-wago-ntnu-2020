import time
from threading import Thread


def method1():
    for x in range(1, 100000000):
        if x % 100000 == 0:
            print("Metod1: " + str(x))
        y = 2 + x ** 2 - x ** 10 - 15000
        z = y ** 15 - 15000 + (x - y)
    print("Done")


def method2():
    while True:
        print("method2")
        time.sleep(1)


t1 = Thread(target=method1, args=())
t1.start()
t2 = Thread(target=method2, args=())
t2.start()


t1.join()
t2.join()
