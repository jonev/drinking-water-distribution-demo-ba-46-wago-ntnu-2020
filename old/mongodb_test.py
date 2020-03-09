import bson
import time
from pymongo import MongoClient
from plclib.motor_control import MotorControlDigital
from plclib.alarm_digital import AlarmDigital
from plclib.timer import Timer

inputFromUser = "ok"
motor = MotorControlDigital(tag="motortag", alarmDigitalStartFailed=AlarmDigital(Timer(0.0, 0.0)))
client = MongoClient(host="mongo", port=27017, username="root", password="example")
db = client.testdb
t = Timer(10.0, 20.0)

while inputFromUser != "exit":
    inputFromUser = input("exit, read, write, replace ")
    if inputFromUser == "exit":
        break
    if inputFromUser == "read":
        result = db.testtable.find_one({"_id": "motortag2"})
        print(result)
        updated = MotorControlDigital.getMotorControlDigital(result)
        print(updated.getBSON().__str__())

    if inputFromUser == "write":
        result = db.testtable.insert_one(motor.getBSON())
        print(result)

    if inputFromUser == "replace":
        motor.setAuto(True)
        result = db.testtable.replace_one({"_id": motor.tag}, motor.getBSON(), upsert=True)
        print(result)

client.close()
