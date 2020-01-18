from plclib.motor_control import MotorControl


def run():
    instance = MotorControl("P3")
    print(instance.tag)
    print(instance.out)
    instance.start()
    print(instance.out)
    instance.stop()
    print(instance.out)
