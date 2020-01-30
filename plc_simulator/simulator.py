""" This file is for simulation inputs and outputs on the plc
"""


def simulatorMethod(simlock, runflag, digitalInputs):
    print("Starting Simulator")
    while runflag[0]:
        inputFromUser = input("Key 0 to exit, Key 1 to 9 is digital inputs, please provide input: ")
        with simlock:
            if inputFromUser == "0":
                runflag[0] = False
            if inputFromUser == "1":
                digitalInputs[0] = not digitalInputs[0]
            if inputFromUser == "2":
                digitalInputs[1] = not digitalInputs[1]
            if inputFromUser == "3":
                digitalInputs[2] = not digitalInputs[2]
            if inputFromUser == "4":
                digitalInputs[3] = not digitalInputs[3]
            if inputFromUser == "5":
                digitalInputs[4] = not digitalInputs[4]
            if inputFromUser == "6":
                digitalInputs[5] = not digitalInputs[5]
            if inputFromUser == "7":
                digitalInputs[6] = not digitalInputs[6]
            if inputFromUser == "8":
                digitalInputs[7] = not digitalInputs[7]
            if inputFromUser == "9":
                digitalInputs[8] = not digitalInputs[8]
    print("Stopping Simulator")
