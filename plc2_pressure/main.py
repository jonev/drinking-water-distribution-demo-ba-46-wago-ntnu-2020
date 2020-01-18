from plclib.motor_control import MotorControl


def run():
    m = MotorControl("P2")
    print(m.tag)
    print(m.out)
    m.start()
    print(m.out)
    m.stop()
    print(m.out)
