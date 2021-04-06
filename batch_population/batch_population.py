"""
@author: Sam Parry
"""

import json
import os
import shutil
import sys

# 5 variable hyperparams
pop_size = [100, 300]
stack_size = [50, 100]
differential_weight = [0.1, 1.0]
crossover_rate = [0.4, 0.8]
mutation_rate = [0.4, 0.8]

""" For reference
original_params = [500, 120, 0.1, 0.8, 0.2]
number_of_trials = 5
"""

# file paths
chpc_parent_dir = "/uufs/chpc.utah.edu/common/home/u1008557/" + sys.argv[-1]


# alters the original beam_bending.json file
# original beam_bending.json file is represented by a dict
# key values are changed via input params
# returns a json object with indent=4
def modifyBendingBeam(params, filepath):
    pop_size, stack_size, differential_weight, crossover_rate, mutation_rate, = params[:]
    dictKeys = ["pop_size", "stack_size", "differential_weight", "crossover_rate", "mutation_rate"]

    # copy of the original beam_bending.json expressed as a dictionary
    new_json_as_dict = {
        "problem": "beam_bending",
        "operators": ["+", "-", "*", "/", "^"],
        "problem_args": [5.0e-2, 0.0, 10.0, 5],
        "hyperparams": {
            "pop_size": 500,
            "stack_size": 120,
            "max_generations": 100000,
            "fitness_threshold": 1e-12,
            "stagnation_threshold": 100000,
            "differential_weight": 0.1,
            "check_frequency": 10,
            "min_generations": 10,
            "crossover_rate": 0.8,
            "mutation_rate": 0.2,
            "evolution_algorithm": "DeterministicCrowding"
        },
        "result_file": "beam_bending.res.json",
        "log_file": "beam_bending",
        "checkpoint_file": "beam_bending"
    }

    # change values of specified hyperparameters
    for i in range(len(params)):
        new_json_as_dict["hyperparams"][dictKeys[i]] = params[i]

    # Write new json file to given directory
    filename = filepath + "/beam_bending.json"
    with open(filename, 'w') as outfile:
        json.dump(new_json_as_dict, outfile, indent=4)


# create a directory and sub directories in a given location
# calls modifyBeamBending and passes the subfolder file path so the json can we written
def createDirectories(params, parent_dir, folder, number_of_trials):
    path = os.path.join(parent_dir, folder) #i.e. /uufs/chpc.utah.edu/common/home/u1008557/tuning_params/00000
    print(path)
    # create the directory "folder" in "parent_dir"
    # if the directory already exists, deletes existing
    # directory and recreates a new one
    try:
        os.mkdir(path)
    except:
       shutil.rmtree(path)
       os.mkdir(path)

    # create subfolders for each trial run
    subfolder_parent_dir = parent_dir + "/" + folder

    # files to copy into new directories
    file1 = "/uufs/chpc.utah.edu/common/home/u1008557/models/fifth_deriv_penalty/doit.slurm"

    # subfolders names trial1, trial2 etc.
    for i in range(number_of_trials):
        subfolder = "trial" + str(i)
        filepath = os.path.join(subfolder_parent_dir, subfolder)
        os.mkdir(filepath)

        # write json to new trial folder
        modifyBendingBeam(params, filepath)

        # copy over .slurm file
        shutil.copy(file1, filepath)

# creates a new set of parameters for each possible combination (160 in total)
# encapsulate this into a function later
for a in range(len(pop_size)):
    for b in range(len(stack_size)):
        for c in range(len(differential_weight)):
            for d in range(len(crossover_rate)):
                for e in range(len(mutation_rate)):
                    params = [pop_size[a], stack_size[b], differential_weight[c], crossover_rate[d], mutation_rate[e]]

                    folder = str(a) + str(b) + str(c) + str(d) + str(e)

                    # function call
                    createDirectories(params, chpc_parent_dir, folder, 5)
