from plclib.motor_control import MotorControl


def run():
    instance = MotorControl("P3")
    print(instance.tag)
    print(instance.controlValue)
    instance.start()
    print(instance.controlValue)
    instance.stop()
    print(instance.controlValue)
