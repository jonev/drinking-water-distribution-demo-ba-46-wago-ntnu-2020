#!/usr/bin/env bash
import os
import time

print("Hello main")
path1 = "./ver1/hello1.py"
path2 = "./ver2/hello1.py"
runpath = path1

modified_time = 0
modified_time_lastScan = 0

while True:
    # Read last changed
    path1time = os.stat(path1).st_mtime
    path2time = os.stat(path2).st_mtime

    # Check if newer
    if path1time > path2time:
        runpath = path1
    else:
        runpath = path2

    # Running newest version
    result = os.system("python " + runpath)  # Works: Return 0 on ok and != 0 when error
    print(result)
    if result != 0:
        if runpath == path1:
            runpath = path2
        else:
            runpath = path1
        os.system("python " + runpath)

    time.sleep(2.0)
    # inputed = input("Enter filename + .py")
