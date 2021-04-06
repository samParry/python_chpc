# -*- coding: utf-8 -*-
""" @author: Sam Parry, Erick Solum """

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from problems.beam_bending import analytic_solution
from bingo.evolutionary_optimizers.parallel_archipelago import load_parallel_archipelago_from_file
from bingo.evolutionary_optimizers.parallel_archipelago import *
import sys
import os
import shutil
import csv
import re
from sympy import simplify, expand
from sympy.parsing.sympy_parser import *

matplotlib.use('Agg')

"""
INPUTS: Test directory path relative to home dir.
        subtest folder names as a list. i.e. list([1, 2, 3])
Start in the test folder named for the hyperparameter
    crossover_rate
    differential_weight
    mutation_rate
"""


class Navigation:
    """
    Defines an object containg all the filepaths required to generate and collect the test results of
    a specified binary test folder.
    Requires the tests directory name as a String input to collect_results.py
    """

    def __init__(self, testPath, binary):
        """
        Defines the file paths required to collect test results from the 5 trial runs
        of a specific combination of parameters (binary)

        :param testPath: Absolute directory path for current generation of tests (binaries)
        :param binary: Current binary test directory.
        """

        """ String Examples
        testPath: '/uufs/chpc.utah.edu/common/home/u1008557/tuning_params/
        csvPath: '/uufs/chpc.utah.edu/common/home/u1008557/tuning_params/Fitness_Data.csv
        plotsPath: '/uufs/chpc.utah.edu/common/home/u1008557/tuning_params/plots/
        binaryPath: '/uufs/chpc.utah.edu/common/home/u1008557/tuning_params/10101
        trialPath: '/uufs/chpc.utah.edu/common/home/u1008557/tuning_params/10101/trial1
        """

        # File Paths
        self.testPath = testPath
        self.csvPath = testPath + "Fitness_Data.csv"
        self.plotsPath = testPath + "plots/"
        self.binary = binary
        self.binaryPath = ""
        self.trialPaths = []
        self.set_paths()  # populate trialPaths and binaryPath

        # execute result collection
        self.collect_results()

    def set_paths(self):
        """ Generates file paths for a new binary directory and its trials """
        self.binaryPath = self.testPath + self.binary
        for i in range(5):
            self.trialPaths.append(self.binaryPath + "/trial" + str(i))

    @staticmethod
    def get_pkl_input():
        """
        Scans the current directory and returns the most recent beam_bending_#####.pkl file
        This file is a required input for the plotting function and simplificaiton function
        :return: input filepath for plot_from_pkl.py
        """
        bending_names = []
        with os.scandir() as it:
            for entry in it:
                # Filters the files that we don't need, and gives us the 2 .pkl files in order.
                if entry.name.startswith("beam_bending") and entry.is_file() and entry.name.endswith('.pkl'):
                    bending_names.append(entry.name)
        if not bending_names:
            return None  # handles the case that a test has no pkl file and must be skipped
        return bending_names[-1]

    def plot_from_pickle(self, beamBendingPkl):
        """
        Generates a plot of the trial results named "best_individual.png" within the trial folder.
        Copies the plot into the plots folder inside the testing parent directory
        :param beamBendingPkl: file name of the .pkl file containing test results
        """

        if beamBendingPkl is None:  # handles missing .pkl file
            return None

        # read bingo pickle file and retrieve best model
        archipelago = load_parallel_archipelago_from_file(beamBendingPkl)
        best_ind = archipelago.get_best_individual()

        L = 10.
        k = 5.e-5
        x = np.linspace(0., L, 64).reshape([64, 1])
        yan = analytic_solution(x, k, L)
        y = best_ind.evaluate_equation_at(x)

        # plot the training data
        X_a = np.linspace(0, 10, 5)
        Y_a = analytic_solution(X_a, 5e-5, 10)

        plt.figure()
        plt.plot(x, yan, 'r-', label='Analytical Solution')
        plt.plot(X_a, Y_a, 'gx', label='Training Data Points')
        plt.plot(x, y, 'b-', label='Best GPSR Model')
        plt.xlabel('x')
        plt.ylabel('displacement')
        plt.legend()
        plt.savefig('best_individual')
        plt.close()

        # copy plot to 'plots' directory in testing dir
        cwd = os.getcwd()
        plotName = self.binary + "_" + cwd[-1]
        src = cwd + "/best_individual.png"
        dst = self.plotsPath + plotName + ".png"
        shutil.copyfile(src, dst)

    def write_results(self, beamBendingPkl):
        """
        Writes the test results to the .csv in the test parent directory
        :param beamBendingPkl: Filename of the .pkl file containing test results.
        """
        if beamBendingPkl is None:  # handles missing .pkl file
            return None

        # simplify equation
        archipelago = load_parallel_archipelago_from_file(beamBendingPkl)
        best_ind = archipelago.get_best_individual()
        polynomial = Simplification(str(best_ind)).result

        # write test results to the csv
        with open(self.csvPath, 'a') as csvfile:
            fieldNames = ['binary', 'fitness', 'generations', 'f(X_0)']
            w = csv.DictWriter(csvfile, dialect='excel', fieldnames=fieldNames)
            w.writerow({'binary': self.binary, 'fitness': best_ind.fitness,
                        'generations': archipelago.generational_age, 'f(X_0)': polynomial})

    def collect_results(self):
        """ Collect the plots and results from each trial """
        for tpath in self.trialPaths:
            os.chdir(tpath)
            beamBendingPkl = self.get_pkl_input()
            self.plot_from_pickle(beamBendingPkl)
            self.write_results(beamBendingPkl)


class Simplification:
    """
    Converts an polynomial expression into a simplified and expanded polynomial form.
    Intented for use accepting equations from BINGO
    """

    def __init__(self, simplification_input):
        """
        Accepts the string representation of a polynomial expression from BINGO.
        Converts the polynomial into an expanded form stored as the attribute 'result'
        :param simplification_input: String polynomial expression
        """
        if isinstance(simplification_input, str):
            self.input_string = simplification_input
        else:
            try:
                self.input_string = str(simplification_input)
            except:
                raise ValueError("Input must be a String representation of a polynomial")
        self.v_filtered = ''
        self.result = self.run_simplify()

    def filtered_list(self, input_str):
        """
        finds all the floats inside of the string output. It will prioritize the earlier or's. (Seperated by | )
        Find all gives us all of the numbers, including repeats.
        """
        v = re.findall('[0-9]+\.[0-9]+[e]...|'
                       '\-[0-9]+\.[0-9]+[e]...|'
                       '[0-9]+\.[0-9]+|'
                       '\-[0-9]+\.[0-9]+'
                       , input_str)
        vf = list(set(v))
        return vf

    def run_simplify(self):
        """
        Performs symbolic simplification on the polynomial.
        :return: expanded polynomial
        """
        self.v_filtered = self.filtered_list(self.input_string)
        expr_v1 = self.str_processing(self.input_string)
        standard_trans = (convert_xor, auto_symbol,
                          auto_number)
        expr_v2 = parse_expr(expr_v1, transformations=standard_trans)
        expr_v3 = simplify(expr_v2, evaluate=False, symbolic=True)
        expr_v4 = expand(expr_v3, complex=False)

        # remove imaginary number token 'I'
        # expr_v4 = re.sub('[*][I]','',expr_v4)
        expr_v4 = str(expr_v4).replace('*I', '')
        return expr_v4

    def str_processing(self, expr, x_type='x'):
        """ Clean up operation to make sure that sympy can understand the string. """
        expr_sp = re.sub(x_type, 'x', expr)
        expr_v1 = re.sub('[)][(]', ')*(', expr_sp)
        return expr_v1


def create_csv(csvPath):
    """
    Creates a new csv file inside the test directory and writes a header in the file.
    If a csv already exists then it is removed and recreated.
    """
    if os.path.exists(csvPath):
        os.remove(csvPath)

    # write fitness data headers to a .csv file
    with open(csvPath, 'a') as csvfile:
        fieldsnames = ['binary', 'fitness', 'generations', 'f(X_0)']
        w = csv.DictWriter(csvfile, dialect='excel', fieldnames=fieldsnames)
        w.writeheader()


def create_plots_dir(plotsPath):
    """
    Creates a new Directory names 'plots' inside the test directory.
    Removes and recreates the directory if it already exists.
    """
    if os.path.isdir(plotsPath):
        shutil.rmtree(plotsPath)
    os.mkdir(plotsPath)


def create_binaries():
    """
    Create the 32 binaries from 00000 - 11111
    :return: list of binaries
    """
    binaries = []
    for a in (0, 1):  # create array of binary files
        for b in (0, 1):
            for c in (0, 1):
                for d in (0, 1):
                    for e in (0, 1):
                        binaries.append(str(a) + str(b) + str(c) + str(d) + str(e))
    return binaries


def main():
    # Ensure user gave an input
    if sys.argv[-1] == __file__ or sys.argv[-2] == __file__:
        print("Input name of test directory")
        sys.exit()

    # define directory paths
    testDir = sys.argv[-2]  # The test dir is assumed to be in the home dir
    testPath = "/uufs/chpc.utah.edu/common/home/u1008557/" + testDir + "/"
    plotsPath = testPath + "plots"
    csvPath = testPath + "Fitness_Data.csv"

    # create plot directory and Fitness_Data.csv
    create_csv(csvPath)
    create_plots_dir(plotsPath)

    # execute navigation
    values = map(str, sys.argv[-1]) # convert input list to strings
    for value in values:
        Navigation(testPath, value)


if __name__ == "__main__":
    main()
