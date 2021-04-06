# -*- coding: utf-8 -*-
"""@author: Sam"""
import shutil
import os
import sys

#INPUT1: highest binary folder that we DONT WANT TO RUN
#INPUT2: parent directory of containing the binaries

# ensures input is given
input = sys.argv[-1]
if (input == __file__):
    print("Input parent directory and a binary as a string\nAll binaries up to & including the input binary will be skipped")
    sys.exit()

doit1File = "/uufs/chpc.utah.edu/common/home/u1008557/models/fifth_deriv_penalty/doit_notch272.slurm"
doit2File = "/uufs/chpc.utah.edu/common/home/u1008557/models/fifth_deriv_penalty/doit_notch273.slurm"
doit3File = "/uufs/chpc.utah.edu/common/home/u1008557/models/fifth_deriv_penalty/doit_notch274.slurm"

# flag boolean determins when the threshold input has been reached.
# all binaries after the threshold will be added to the array
metThreshold = False
binariesToChange = []
for a in (0, 1):
    for b in (0, 1):
        for c in (0, 1):
            for d in (0, 1):
                for e in (0, 1):
                    curBinary = str(a) + str(b) + str(c) + str(d) + str(e)
                    if metThreshold:
                        binariesToChange.append(curBinary)
                    else:
                        if curBinary == input:
                            metThreshold = True

# keeps track of which binaries have which node
notch272 = []
notch273 = []
notch274 = []

trials = ["trial0", "trial1", "trial2", "trial3", "trial4"]
biLength = len(binariesToChange)
for i in range(biLength):
    #determine which doit file to use
    if (i < biLength//3):
        notch272.append(binariesToChange[i])
        newDoit = doit1File
    elif (i < 2*biLength//3):
        notch273.append(binariesToChange[i])
        newDoit = doit2File
    else:
        notch274.append(binariesToChange[i])
        newDoit = doit3File
        
    for j in range(len(trials)):
        # replace existing doit.slurm with new doit.slurm
        dest = "/uufs/chpc.utah.edu/common/home/u1008557/" + sys.argv[-2] + "/" + binariesToChange[i] + "/" + trials[j] + "/doit.slurm"
        os.remove(dest)
        shutil.copy(newDoit, dest)

# print which binary is going to which node
print("\nnotch272")
print(notch272) 
print("\nnotch273")
print(notch273) 
print("\nnotch274")
print(notch274) 
print("\n")



