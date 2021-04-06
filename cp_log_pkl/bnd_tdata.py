# -*- coding: utf-8 -*-
""" @author: Sam """

import shutil
import os

# directory labels
scratch = "/scratch/kingspeak/serial/u1008557/"
trials = ['trial{0}'.format(i) for i in range(1,31)]
destPath = "/uufs/chpc.utah.edu/common/home/u1008557/tests/bnd_tdata/"
tValues = ["t2", "t4", "t4-new", "t8", "t16", "t32", "t64"]

for t in tValues:
    print(t)
    for trial in trials:
        dest = "{0}/{1}/{2}/".format(destPath, t, trial)

        # get jobID's from the .out file within each trial folder
        os.chdir(dest)
        with os.scandir() as it:
            for entry in it:
                if entry.name.endswith('.out-notch204'):
                    job_id = entry.name.split('.')[0]
        source = scratch + job_id + "/"

        # copies all .pkl & .log files from the scratch dir to the test dir.
        for filename in os.listdir(source):
            if filename.endswith('.pkl'):
                fileSource = source + filename
                shutil.copy(fileSource, dest)
            if filename.endswith('.log'):
                fileSource = source + filename
                shutil.copy(fileSource, dest)
