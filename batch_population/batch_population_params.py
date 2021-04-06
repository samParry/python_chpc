# -*- coding: utf-8 -*-
""" @author: Sam """

import json
import os
import shutil
import sys

"""
Inputs:
Parameter being tests: diff, cross, mut
Slurm file: 272, 273, 274
"""


def modifyBendingBeam(param, trialPath):
    """
    alters the original beam_bending.json file
    original beam_bending.json file is represented by a dict
    key values are changed via input params
    returns a json object with indent=4

    :param param: Hyperparameter
    :param trialPath: location of current test folder
    """
    if sys.argv[-2] == "diff":
        dictKey = "differential_weight"
    elif sys.argv[-2] == "cross":
        dictKey = "crossover_rate"
    else:
        dictKey = "mutation_rate"

    # copy of the original beam_bending.json expressed as a dictionary
    new_json_as_dict = {
        "problem": "beam_bending",
        "operators": ["+", "-", "*", "/", "^"],
        "problem_args": [5.0e-2, 0.0, 10.0, 5],
        "hyperparams": {
            "pop_size": 100,
            "stack_size": 50,
            "max_generations": 100000,
            "fitness_threshold": 1e-12,
            "stagnation_threshold": 100000,
            "differential_weight": 0.1,
            "check_frequency": 5,
            "min_generations": 10,
            "crossover_rate": 0.4,
            "mutation_rate": 0.4,
            "evolution_algorithm": "DeterministicCrowding"
        },
        "result_file": "beam_bending.res.json",
        "log_file": "beam_bending",
        "checkpoint_file": "beam_bending"
    }

    # change values of specified hyperparameters
    new_json_as_dict["hyperparams"][dictKey] = param

    # Write new json file to given directory
    filename = trialPath + "/beam_bending.json"
    with open(filename, 'w') as outfile:
        json.dump(new_json_as_dict, outfile, indent=4)


def createDirectory(dirPath):
    """
    Create a directory from an absolute filepath
    If the directory already exists then it is repalced by an empty directory.

    :param dirPath: Filepath to create
    """
    try:
        os.mkdir(dirPath)
    except FileExistsError:
        shutil.rmtree(dirPath)
        os.mkdir(dirPath)


def populateTests(params, valuePath, slurm):
    """
    create a directory and sub directories in a given location
    calls modifyBeamBending and passes the subfolder file path so the json can we written

    :param params: Hyperparameters for the current test
    :param valuePath: Name of the new generation of tests where all these files will be placed
    :param slurm: filepath to the doit.slurm file
    """
    # Create paths for new value folder
    createDirectory(valuePath)

    # subfolders names trial1, trial2 etc.Ya
    for trialNumber in range(5):
        trialPath = "{0}trial{1}".format(valuePath, trialNumber)
        os.mkdir(trialPath)
        # write json to new trial folder
        modifyBendingBeam(params, trialPath)
        # copy over .py and .slurm files
        shutil.copy(slurm, trialPath)


def main():
    """ Its a main method. What do you think it does"""
    # hard coded test_values to undergo training data variation testing
    if sys.argv[-2] == "diff":
        testSuperPath = "/uufs/chpc.utah.edu/common/home/u1008557/param_study/differential_weight/"
        test_values = ["0.2", "0.4", "0.6", "0.8"]
    elif sys.argv[-2] == "cross":
        testSuperPath = "/uufs/chpc.utah.edu/common/home/u1008557/param_study/crossover_rate/"
        test_values = ["0.3", "0.5", "0.6", "0.7", "0.9"]
    else:
        testSuperPath = "/uufs/chpc.utah.edu/common/home/u1008557/param_study/mutation_rate/"
        test_values = ["0.3", "0.5", "0.6", "0.7", "0.9"]

    # create testing directory in /uufs/chpc.utah.edu/common/home/u1008557/
    createDirectory(testSuperPath)

    # determine slurmPath from input
    if sys.argv[-1] == "272":
        slurm = "/uufs/chpc.utah.edu/common/home/u1008557/models/fifth_deriv_penalty/doit_notch272.slurm"
    elif sys.argv[-1] == "273":
        slurm = "/uufs/chpc.utah.edu/common/home/u1008557/models/fifth_deriv_penalty/doit_notch273.slurm"
    else:
        slurm = "/uufs/chpc.utah.edu/common/home/u1008557/models/fifth_deriv_penalty/doit_notch274.slurm"

    # make directories for each value
    for n in range(len(test_values)):
        populateTests(test_values[n], testSuperPath + test_values[n] + "/", slurm)


if __name__ == "__main__":
    main()
