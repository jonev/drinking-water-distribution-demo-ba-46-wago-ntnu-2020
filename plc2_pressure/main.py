from threading import Lock, Thread
import time
from plclib.motor_control import MotorControlDigital
from plclib.alarm_digital import AlarmDigital
from plclib.timer import Timer
from plc_simulator import simulator
from plclib import util as u

runflag = [True]
digitalInputs = [False, False, False, False, False, False, False, False, False, False]
digitalOutputs = [False, False, False, False, False, False, False, False, False, False]
simlock = Lock()


def run():
    # Starting simulator
    simulatorThread = Thread(
        target=simulator.simulatorMethod, args=(simlock, runflag, digitalInputs)
    )
    simulatorThread.start()

    # Proposed structure
    # Init instances
    m1 = MotorControlDigital("M1")
    m1AlarmStart = AlarmDigital(
        Timer(5.0, 5.0)
    )  # Alarm if open command is sat and open feedback is not received and visa versa
    m1AlarmStop = AlarmDigital(
        Timer(5.0, 5.0)
    )  # Alarm if close command is sat and close feedback is not received and visa versa

    while runflag[0]:

        # Read inputs
        with simlock:
            m1.setAuto(digitalInputs[0])  # Set motor in auto or manual mode, typically from HMI
            if digitalInputs[1]:  # Start command in auto, typically from digital or analog input
                m1.startCommandAuto()
                digitalInputs[1] = False
            if digitalInputs[2]:  # Stop command in auto, typically from digital or analog input
                m1.stopCommandAuto()
                digitalInputs[2] = False

            # Run alarm logic
            m1AlarmStart.input(m1.controlValue != digitalInputs[3])
            m1AlarmStop.input(m1.controlValue != digitalInputs[4])

            m1.interlock(not m1AlarmStart.alarm and not m1AlarmStop.alarm)

        # Run control logic ??

        # Write outputs
        digitalOutputs[0] = m1.controlValue

        print("m1AlarmOpen.alarm", m1AlarmStart.alarm)
        print("m1AlarmClose.alarm", m1AlarmStop.alarm)
        print(digitalOutputs)
        time.sleep(1)  # Sampletime 1 sec

    print("Waiting for simulator thread to stop....")
    simulatorThread.join()
    print("Safely exiting...")

