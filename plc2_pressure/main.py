from threading import Lock, Thread
import time
from plclib.motor_control import MotorControlDigital
from plclib.alarm_digital import AlarmDigital
from plclib.analog_signal import AnalogSignal
from plclib.timer import Timer
from plc_simulator import simulator
from plclib.utils import Scaling
import os

dev = True
runflag = [True]
digitalInputs = [False, False, False, False, False, False, False, False, False, False]
analogInputs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
digitalOutputs = [False, False, False, False, False, False, False, False, False, False]
analogOutputs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
simlock = Lock()


def run():
    if dev:
        # Starting simulator
        simulatorThread = Thread(
            target=simulator.simulatorMethod, args=(simlock, runflag, digitalInputs, analogInputs)
        )
        simulatorThread.start()

    # Proposed structure
    # Init instances
    analogSignalTest = AnalogSignal(
        tag="Analog Signal Test",
        alarmHigh=AlarmDigital(Timer(5.0, 5.0)),
        alarmLow=AlarmDigital(Timer(5.0, 5.0)),
        scaling=Scaling(0.0, 1.0, 0.0, 100.0),
    )
    motorControlDigitalTest = MotorControlDigital(tag="Motor control digital test")

    while runflag[0]:

        # Read inputs
        with simlock:
            analogSignalTest.rawInput(analogInputs[0])
            analogSignalTest.setSimulationMode(digitalInputs[0])
            analogSignalTest.setSimulationValue(analogInputs[1])
            analogSignalTest.setAlarmHighLimit(analogInputs[2])
            analogSignalTest.setAlarmLowLimit(analogInputs[3])

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

        # Write outputs
        analogOutputs[0] = analogSignalTest.output
        digitalOutputs[0] = motorControlDigitalTest.controlValue

        print("digitalInputs:", digitalInputs)
        print("analogInputs:", analogInputs)
        print("digitalOutputs:", digitalOutputs)
        time.sleep(2)  # Sampletime 2 sec

    if dev:
        print("Waiting for simulator thread to stop....")
        simulatorThread.join()
        print("Safely exiting...")

