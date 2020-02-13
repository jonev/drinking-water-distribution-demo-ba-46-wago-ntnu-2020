import os
import time

from pymongo import MongoClient
from plclib.mqtt_client import MQTTClient

# from pymodbus.client.sync import ModbusUdpClient
from opcua import Client, ua
from threading import Thread

from plclib.motor_control import MotorControlDigital
from plclib.alarm_digital import AlarmDigital
from plclib.analog_signal import AnalogSignal
from plclib.timer import Timer
from plclib.utils import Scaling

mongodbClient = MongoClient(host="mongo", port=27017, username="root", password="example")
db = mongodbClient["states"]
mqtt = MQTTClient("broker.hivemq.com", 1883, 60, ["wago/ba/plc2/in/#"])
# UNIT = 0x1
# clientIO = ModbusUdpClient("192.168.0.15", port=50300)
# clientHMI = ModbusUdpClient("192.168.0.15", port=50301)
OPCClient = Client("opc.tcp://192.168.0.15:4840")
OPCClient.set_user("admin")
OPCClient.set_password("wago")
ns = 4
HmiId = "|var|WAGO 750-8214 PFC200 G2 2ETH RS CAN.PFCx00_SmartCoupler.HMI"
variables = {}


def getChildrenRecursive(child):
    children = child.get_children()
    if len(children) == 0:
        variables[child.nodeid.Identifier.replace(HmiId + ".", "")] = child
    else:
        for c in children:
            getChildrenRecursive(c)


# dev = False
runflag = [True]
digitalInputs = [False, False, False, False, False, False, False, False, False, False]
analogInputs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
digitalOutputs = [False, False, False, False, False, False, False, False]
analogOutputs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
hmiOutput = [0, 0, 0, 0, 0, 0, 0, 0, 0]
mqttThread = 0
scantime = time.time()
timeLastScan = time.time()


def runLoop():
    global timeLastScan
    try:
        OPCClient.connect()
        HMI = OPCClient.get_node("ns=" + str(ns) + ";s=" + HmiId)
        for child in HMI.get_children():
            getChildrenRecursive(child)

        mqttThread = Thread(target=mqtt.loopForever, args=())
        mqttThread.start()
        time.sleep(2)  # Time to connect mqtt
        mqtt.publish("wago/ba/plc2/out/logg", "Starting run method...")
        # Init instances
        # Restore state, if exist
        motorControlDigitalTest = []
        readDbResult = db.motors.find_one({"_id": "MotorControlDigitalTest"})
        if readDbResult is None:
            motorControlDigitalTest = MotorControlDigital(
                tag="MotorControlDigitalTest",
                alarmDigitalStartFailed=AlarmDigital(Timer(10.0, 0.0)),
            )
        else:
            motorControlDigitalTest = MotorControlDigital.getMotorControlDigital(readDbResult)

        # Time to startup
        scanNr = 0
        while runflag[0]:
            scanNr = scanNr + 1
            mqtt.publish("wago/ba/plc2/out/logg", "Scan start nr: " + str(scanNr))
            # Read inputs
            # Reading slot 2 - 8 Analog inputs
            # readResult = clientIO.read_input_registers(17, 8, unit=UNIT)
            # analogInputs = readResult.registers
            # Reading HMI
            # Float? https://stackoverflow.com/questions/30784965/pymodbus-read-write-floats-real
            # readResult = clientHMI.read_input_registers(1, 10, unit=UNIT)
            # hmiInput = readResult.registers

            # Motor
            # TODO need a better way to do this:
            try:
                motorControlDigitalTest.setAuto(
                    variables["MotorControlDigitalTest.auto"].get_value()
                )  # Set motor in auto or manual mode, typically from HMI

                if variables[
                    "MotorControlDigitalTest.startCommandManual"
                ].get_value():  # Start command in auto, typically from digital or analog input
                    motorControlDigitalTest.startCommandManual()
                    variables["MotorControlDigitalTest.startCommandManual"].set_value(False)

                if variables[
                    "MotorControlDigitalTest.stopCommandManual"
                ].get_value():  # Stop command in auto, typically from digital or analog input
                    motorControlDigitalTest.stopCommandManual()
                    variables["MotorControlDigitalTest.stopCommandManual"].set_value(False)
                if variables[
                    "MotorControlDigitalTest.startCommandAuto"
                ].get_value():  # Start command in auto, typically from digital or analog input
                    motorControlDigitalTest.startCommandAuto()
                    variables["MotorControlDigitalTest.startCommandAuto"].set_value(False)
                if variables[
                    "MotorControlDigitalTest.stopCommandAuto"
                ].get_value():  # Stop command in auto, typically from digital or analog input
                    motorControlDigitalTest.stopCommandAuto()
                    variables["MotorControlDigitalTest.stopCommandAuto"].set_value(False)

                motorControlDigitalTest.interlock(True)
                motorControlDigitalTest.setStartedFeedback(True)

                # Write outputs
                variables["MotorControlDigitalTest.controlValue"].set_value(
                    motorControlDigitalTest.controlValue
                )
                variables["MotorControlDigitalTest.tag"].set_value(
                    motorControlDigitalTest.tag, varianttype=ua.VariantType.String
                )
            except Exception as e:
                mqtt.publish("wago/ba/plc2/out/exceptions", e.__str__())

            # Writing slot 1 - 8 Digital outputs
            # result = clientIO.write_registers(1, digitalOutputs, unit=0x01)
            # Writing HMI tags
            # result = clientHMI.write_registers(1, hmiOutput, unit=0x01)
            # if result.isError():
            #    raise Exception("Writing digital outputs failed")

            # Publishing states over mqtt
            mqtt.publish(
                "wago/ba/plc2/out/MotorControlDigital", motorControlDigitalTest.getBSON().__str__()
            )
            # mqtt.publish("wago/ba/plc2/out/hmi/in", "Hmi Input: " + hmiInput.__str__())
            # mqtt.publish("wago/ba/plc2/out/hmi/out", "Hmi Output: " + hmiOutput.__str__())
            # mqtt.publish("wago/ba/plc2/out/di", "Digital Input: " + digitalInputs.__str__())
            # mqtt.publish("wago/ba/plc2/out/ai", "Analog Input: " + analogInputs.__str__())
            # mqtt.publish("wago/ba/plc2/out/do", "Digital Output: " + digitalOutputs.__str__())

            # Storing state in local db
            result = db.motors.replace_one(
                {"_id": motorControlDigitalTest.tag}, motorControlDigitalTest.getBSON(), upsert=True
            )
            time.sleep(0.01)  # Sampletime 5 sec - for testing
            t = time.time()
            scantime = t - timeLastScan
            timeLastScan = t
            mqtt.publish("wago/ba/plc2/out/scantime", scantime.__str__())
            db.scantime.insert_one({"scantime": scantime})

    finally:
        OPCClient.disconnect()
        mqtt.disconnect()
        mqttThread.join()
