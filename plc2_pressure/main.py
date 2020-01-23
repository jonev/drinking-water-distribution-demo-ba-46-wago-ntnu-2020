from threading import Lock, Thread
import time
from plclib.motor_control import MotorControl
from plc_simulator import simulator

runflag = [True]
digitalInputs = [False, False, False, False, False, False, False, False, False, False]
simlock = Lock()


def run():
    # Starting simulator
    simulatorThread = Thread(
        target=simulator.simulatorMethod, args=(simlock, runflag, digitalInputs)
    )
    simulatorThread.start()

    # Proposed structure
    m1 = MotorControl("M1")

    while runflag[0]:
        # Init instances

        # Read inputs
        with simlock:
            m1.setAuto(digitalInputs[0])
            if digitalInputs[1]:
                m1.startCommandAuto()
                digitalInputs[1] = False
            if digitalInputs[2]:
                m1.stopCommandAuto()
                digitalInputs[2] = False

            m1.interlock(digitalInputs[3])

        # Run alarm logic

        # Run control logic

        # Write outputs
        print("m1.controlValue", m1.controlValue)
        time.sleep(1)

    print("Waiting for simulator thread to stop....")
    simulatorThread.join()
    print("Safely exiting...")

