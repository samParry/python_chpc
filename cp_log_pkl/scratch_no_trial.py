# -*- coding: utf-8 -*-
# author: Sam Parry u1008557

import shutil
import os

# directory labels
scratch = "/scratch/kingspeak/serial/u1008557/"
test_dir = "bnd_study" # test name is given as an input

binaries = []
for a in (0, 1):  # create array of binary files
    for b in (0, 1):
        for c in (0, 1):
            for d in (0, 1):
                for e in (0, 1):
                    binaries.append(str(a) + str(b) + str(c) + str(d) + str(e))

jobID = []
#  add job ID's to list (add 1 to the final job to avoid an indexing error)
for a in range(1975708, 1975724):
    jobID.append(str(a))
for a in range(1975728, 1975744):
    jobID.append(str(a))
k = 0  # index for the jobID corrosponding to the current test directory

# construct filepaths between each test directory and the corrosponding folder within
# the scratch directory labeled by the tests jobID and containing the relevant .pkl &.log
# required to run plot_from_pickle.py
for i in range(len(binaries)):
    source = scratch + jobID[k] + "/"
    k += 1
    destination = "/uufs/chpc.utah.edu/common/home/u1008557/tests/{0}/{1}/".format(test_dir, binaries[i])

    # copies all files from the scratch dir to the test dir.
    for filename in os.listdir(source):
        fileSource = source + filename
        shutil.copy(fileSource, destination)
