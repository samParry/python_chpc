# -*- coding: utf-8 -*-
""" @author: Sam """

import json
import os
import shutil
import sys

""" INPUTS
Name of new test directory
"""


def modifyBendingBeam(params, problem_args, trialPath):
    """
    alters the original beam_bending.json file
    original beam_bending.json file is represented by a dict
    key values are changed via input params
    returns a json object with indent=4

    :param params: Hyperparameters
    :param problem_args: numbers relevant to beam bending problem
    :param trialPath: location of current test folder
    """
    dictKeys = ["pop_size", "stack_size", "differential_weight", "crossover_rate", "mutation_rate"]

    # copy of the original beam_bending.json expressed as a dictionary
    new_json_as_dict = {
        "problem": "beam_bending",
        "operators": ["+", "-", "*", "/", "^"],
        "problem_args": [5.0e-5, 0.0, 10.0, 5],
        "hyperparams": {
            "pop_size": 500,
            "stack_size": 120,
            "max_generations": 100000,
            "fitness_threshold": 1e-12,
            "stagnation_threshold": 100000,
            "differential_weight": 0.1,
            "check_frequency": 5,
            "min_generations": 1,
            "crossover_rate": 0.8,
            "mutation_rate": 0.2,
            "evolution_algorithm": "DeterministicCrowding"
        },
        "result_file": "beam_bending.res.json",
        "log_file": "beam_bending",
        "checkpoint_file": "beam_bending"
    }

    # change values of specified hyperparameters
    for j in range(len(params)):
        new_json_as_dict["hyperparams"][dictKeys[j]] = params[j]
        new_json_as_dict["problem_args"] = problem_args

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


def populateTests(params, problem_args, newTestDir, binary, slurm):
    """
    create a directory and sub directories in a given location
    calls modifyBeamBending and passes the subfolder file path so the json can we written

    :param params: Hyperparameters for the current test
    :param problem_args: numbers relevant to beam bending problem
    :param newTestDir: Name of the new generation of tests where all these files will be placed
    :param binary: Directory named with a binary (i.e. 00101). Represents a combination of parameters
    :param slurm: filepath to the doit.slurm file
    """
    # Create paths for new binary folder
    binaryPath = newTestDir + binary + "/"
    createDirectory(binaryPath)

    # subfolders names trial1, trial2 etc.Ya
    for trialNumber in range(5):
        trialPath = "{0}trial{1}".format(binaryPath, trialNumber)
        os.mkdir(trialPath)
        # write json to new trial folder
        modifyBendingBeam(params, problem_args, trialPath)
        # copy over .py and .slurm files
        shutil.copy(slurm, trialPath)


def getParams(binary_str):
    """
    constuct the combination of hyperparameters dictated by the binary file.
    :param binary_str: binary representation of params
    :return: parameters that correspont to the binary
    """
    hyperparams = [[100, 300], [50, 100], [0.1, 1], [0.4, 0.8], [0.4, 0.8]]
    params = list()
    m = 0
    for digit in map(int, binary_str):
        params.append(hyperparams[m][digit])
        m += 1
    return params


def main():
    """ Its a main method. What do you think it does"""
    # ensure input is given
    if sys.argv[-1] == __file__:
        print("Must input the name of new test directory")
        sys.exit()

    # hard coded binaries to undergo training data variation testing
    binaries = ["00000", "00001", "00010", "00011", "00111"]

    # create testing directory in /uufs/chpc.utah.edu/common/home/u1008557/
    testSuperPath = "/uufs/chpc.utah.edu/common/home/u1008557/{0}/".format(sys.argv[-1])
    newTestDir = []
    createDirectory(testSuperPath)
    slurmPaths = ["/uufs/chpc.utah.edu/common/home/u1008557/models/fifth_deriv_penalty/doit_notch272.slurm",
                  "/uufs/chpc.utah.edu/common/home/u1008557/models/fifth_deriv_penalty/doit_notch273.slurm",
                  "/uufs/chpc.utah.edu/common/home/u1008557/models/fifth_deriv_penalty/doit_notch274.slurm"]

    # populate new values for the .json file
    k = 5.0e-2
    trainingPoints =[64]
    #trainingPoints = [2, 4, 6, 8, 10, 100]
    problem_args = []
    for points in trainingPoints:
        problem_args.append([k, 0.0, 10.0, points])
        newTestDir.append("{0}t{1}/".format(testSuperPath, points))
        createDirectory(newTestDir[-1])

    # populate tests
    for binary in binaries:
        params = getParams(binary)
        for n in range(len(problem_args)):  # places a binary folder in each training point directory
            slurm = slurmPaths[n // 2]      # distrubute jobs evenly over 3 seperate nodes.
            populateTests(params, problem_args[n], newTestDir[n], binary, slurm)


if __name__ == "__main__":
    main()
