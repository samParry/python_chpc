# -*- coding: utf-8 -*-
"""
Created on Sat Oct  3 16:24:04 2020
Version 10/23/20
@author: Sam
"""
import shutil
import os

# directory labels
scratch = "/scratch/kingspeak/serial/u1008557/"
test_dir = "bnd_study"
trials = ["trial0", "trial1", "trial2", "trial3", "trial4", "trial5", "trial6", "trial7", "trial8", "trial9"]

binaries = []
for a in (0, 1):  # create array of binary files
    for b in (0, 1):
        for c in (0, 1):
            for d in (0, 1):
                for e in (0, 1):
                    binaries.append(str(a) + str(b) + str(c) + str(d) + str(e))

jobID = []
#  add job ID's to list (add 1 to the final job to avoid an indexing error)
for a in range(1967777, 1968077):
    jobID.append(str(a))
k = 0  # index for the jobID corrosponding to the current test directory

# construct filepaths between each test directory and the corrosponding folder within
# the scratch directory labeled by the tests jobID and containing the relevant .pkl &.log
# required to run plot_from_pickle.py
for i in range(len(binaries)):
    for j in range(len(trials)):
        source = scratch + jobID[k] + "/"
        k += 1
        destination = "/uufs/chpc.utah.edu/common/home/u1008557/tests/{0}/{1}/{2}/".format(test_dir, binaries[i], trials[j])

        # copies all files from the scratch dir to the test dir.
        for filename in os.listdir(source):
            fileSource = source + filename
            shutil.copy(fileSource, destination)
