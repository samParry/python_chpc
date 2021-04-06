# -*- coding: utf-8 -*-
"""
Created on Sat Oct  3 16:04:06 2020

@author: Sam
"""

import shutil
import os

doitFile = "/uufs/chpc.utah.edu/common/home/u1008557/models/fifth_deriv_penalty/doit.slurm"

binary = []

for a in (0, 1):
    for b in (0, 1):
        for c in (0, 1):
            for d in (0, 1):
                for e in (0, 1):
                    binary.append(str(a) + str(b) + str(c) + str(d) + str(e))

trials = ["trial0", "trial1", "trial2", "trial3", "trial4"]
for i in range(len(binary)):
    for j in range(len(trials)):
        newFile = "/uufs/chpc.utah.edu/common/home/u1008557/tuning_params/" + binary[i] + "/" + trials[j] + "/doit.slurm"
        os.remove(newFile)
        shutil.copy(doitFile, newFile)
