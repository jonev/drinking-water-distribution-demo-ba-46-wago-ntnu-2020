import os
import time
from pymodbus.client.sync import ModbusTcpClient
from plclib.mqtt_client import MQTTClient
from threading import Lock, Thread
from pymongo import MongoClient

from plclib.motor_control import MotorControlDigital
from plclib.alarm_digital import AlarmDigital
from plclib.analog_signal import AnalogSignal
from plclib.timer import Timer
from plc_simulator import simulator
from plclib.utils import Scaling

mongodbClient = MongoClient(host="mongo", port=27017, username="root", password="example")
db = mongodbClient.testdb
mqtt = MQTTClient("broker.hivemq.com", 1883, 60, ["wago/ba/plc2/in/#"])
UNIT = 0x1
client = ModbusTcpClient("192.168.0.15", port=50200)

# dev = False
runflag = [True]
digitalInputs = [False, False, False, False, False, False, False, False, False, False]
analogInputs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
digitalOutputs = [False, False, False, False, False, False, False, False]
analogOutputs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
simlock = Lock()
simulatorThread = 0
mqttThread = 0


def run():
    # if dev:
    #    # Starting simulator
    #    simulatorThread = Thread(
    #        target=simulator.simulatorMethod, args=(simlock, runflag, digitalInputs, analogInputs)
    #    )
    #    simulatorThread.start()
    mqttThread = Thread(target=mqtt.loopForever, args=())
    mqttThread.start()
    # Proposed structure
    # Init instances
    # Restore state, if exist
    motorControlDigitalTest = []
    readDbResult = db.testtable.find_one({"_id": "Motor control digital test"})
    if readDbResult is None:
        motorControlDigitalTest = MotorControlDigital(
            tag="Motor control digital test", alarmDigitalStartFailed=AlarmDigital(Timer(10.0, 0.0))
        )
    else:
        motorControlDigitalTest = MotorControlDigital.getMotorControlDigital(readDbResult)

    # Time to startup
    time.sleep(2)

    while runflag[0]:

        # Read inputs
        with simlock:
            # Reading slot 2 - 8 Analog inputs
            readResult = client.read_input_registers(17, 8, unit=UNIT)
            analogInputs = readResult.registers

            # Motor
            motorControlDigitalTest.setAuto(
                digitalInputs[1]
            )  # Set motor in auto or manual mode, typically from HMI
            if digitalInputs[2]:  # Start command in auto, typically from digital or analog input
                motorControlDigitalTest.startCommandAuto()
                digitalInputs[2] = False
            if digitalInputs[3]:  # Stop command in auto, typically from digital or analog input
                motorControlDigitalTest.stopCommandAuto()
                digitalInputs[3] = False

        motorControlDigitalTest.interlock(True)
        motorControlDigitalTest.setStartedFeedback(True)

        # Write outputs
        digitalOutputs[0] = motorControlDigitalTest.controlValue

        # Writing slot 1 - 8 Digital outputs
        result = client.write_registers(1, digitalOutputs, unit=0x01)
        print(result.isError())

        # Publishing states over mqtt
        mqtt.publish(
            "wago/ba/plc2/out/MotorControlDigital", motorControlDigitalTest.getBSON().__str__()
        )
        print("digitalInputs:", digitalInputs)
        mqtt.publish("wago/ba/plc2/out", digitalInputs.__str__())
        print("analogInputs:", analogInputs)
        mqtt.publish("wago/ba/plc2/out", analogInputs.__str__())
        print("digitalOutputs:", digitalOutputs)
        mqtt.publish("wago/ba/plc2/out", digitalOutputs.__str__())

        # Storing state in local db
        result = db.testtable.replace_one(
            {"_id": motorControlDigitalTest.tag}, motorControlDigitalTest.getBSON(), upsert=True
        )
        time.sleep(5)  # Sampletime 5 sec - for testing

    mqtt.disconnect()
    mqttThread.join()
    # if dev:
    #    print("Waiting for simulator thread to stop....")
    #    #simulatorThread.join()
    #    print("Safely exiting...")

