# -*- coding: utf-8 -*-
""" @author: Sam """


# copy command: for .pkl and .log
# cp /scratch/kingspeak/serial/u1008557/JOBID#/*.pkl .; 
# cp /scratch/kingspeak/serial/u1008557/JOBID#/*.log .;

import shutil
import os

# directory labels
scratch = "/scratch/kingspeak/serial/u1008557/"
trials = ["trial0", "trial1", "trial2", "trial3", "trial4"]
destPath = "/uufs/chpc.utah.edu/common/home/u1008557/tdata_gen2/"
tValues = ["t2", "t4", "t6", "t8", "t10", "t100"]
binaries = ["00000", "00001", "00010", "00011", "00111"]

jobID = []
#  add job ID's to list. Must be +1 more then the real end point.
for a in range(1776058, 1776208):
    jobID.append(str(a))

k = 0   # index for the jobID corrosponding to the current test directory
for t in tValues:
    for binary in binaries:
        for trial in trials:
            source = scratch + jobID[k] + "/"
            k += 1
            dest = "{0}/{1}/{2}/{3}/".format(destPath, t, binary, trial)

            # copies all .pkl & .log files from the scratch dir to the test dir.
            for filename in os.listdir(source):
                if filename.endswith('.pkl'):
                    fileSource = source + filename
                    shutil.copy(fileSource, dest)
                if filename.endswith('.log'):
                    fileSource = source + filename
                    shutil.copy(fileSource, dest)
