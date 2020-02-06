from plclib.motor_control import MotorControlDigital


def run():
    instance = MotorControlDigital("P3")
    print(instance.tag)
    print(instance.controlValue)
    instance.startCommandAuto()
    print(instance.controlValue)
    instance.stopCommandAuto()
    print(instance.controlValue)
