""" This file is for simulation inputs and outputs on the plc
"""


def simulatorMethod(simlock, runflag, digitalInputs, analogInputs):
    print("Starting Simulator")
    while runflag[0]:
        inputFromUser = input("Key x to exit, Digital input - di, Analog input - ai: ")
        with simlock:
            if inputFromUser == "x":
                runflag[0] = False

            if inputFromUser == "di":
                nr = int(input("Number: "))
                digitalInputs[nr] = not digitalInputs[nr]
            if inputFromUser == "ai+":
                nr = int(input("Number: "))
                analogInputs[nr] = analogInputs[nr] + 10
            if inputFromUser == "ai-":
                nr = int(input("Number: "))
                analogInputs[nr] = analogInputs[nr] - 10

    print("Stopping Simulator")
