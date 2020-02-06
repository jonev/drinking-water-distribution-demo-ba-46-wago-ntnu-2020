import bson
from pymongo import MongoClient
from plclib.motor_control import MotorControlDigital

inputFromUser = "ok"
motor = MotorControlDigital(tag="motortag")
client = MongoClient(host="mongo", port=27017, username="root", password="example")
db = client.testdb

while inputFromUser != "exit":
    inputFromUser = input("exit, read, write ")
    if inputFromUser == "exit":
        break
    if inputFromUser == "read":
        result = db.testtable.find()
        for x in result:
            print(x)

    if inputFromUser == "write":
        result = db.testtable.insert_one(motor.__dict__)
        print(result)

client.close()
