# -*- coding: utf-8 -*-
""" @author: Sam Parry, Erick Solum """

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from problems.beam_bending import analytic_solution
from bingo.evolutionary_optimizers.parallel_archipelago import load_parallel_archipelago_from_file
from bingo.evolutionary_optimizers.parallel_archipelago import *
import os
import re
from sympy import simplify, expand
from sympy.parsing.sympy_parser import *
from sympy.simplify.radsimp import radsimp
from sympy import preorder_traversal, Float
import csv
import string

matplotlib.use('Agg')


class Simplification:
    """
    Converts an polynomial expression into a simplified and expanded polynomial form.
    Intented for use accepting equations from BINGO
    """

    def __init__(self, simplification_input, rounding_num=13):
        """
        Accepts the string representation of a polynomial expression from BINGO.
        Converts the polynomial into an expanded form stored as the attribute 'result'
        :param simplification_input: String polynomial expression
        """
        self.rm = rounding_num
        self.zero_threshold = 1e-50
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

    def invalid_check(self, expr):
        zthreshold = self.zero_threshold
        replacers = []
        for i in expr.expr_free_symbols:
            if i.is_Float:
                if abs(i) <= zthreshold:
                    replacers.append(str(abs(i)))
        expr_str = str(expr)
        for i in replacers:
            expr_str = re.sub(i, '0', expr_str)
        # remove imaginary number token 'I'
        expr_str = re.sub('[*][I]', '', expr_str)
        result = expr_str
        return result

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
        expr_v2 = self.invalid_check(expr_v2)
        expr_v3 = simplify(expr_v2, evaluate=False, symbolic=True)
        expr_v4 = expand(expr_v3, complex=False)
        expr_v5 = expr_v4
        for a in preorder_traversal(expr_v4):
            if isinstance(a, Float):
                expr_v5 = expr_v5.subs(a, round(a, self.rm))
        return expr_v5

    def str_processing(self, expr, x_type='x'):
        """ Clean up operation to make sure that sympy can understand the string. """
        expr_sp = re.sub(x_type, 'x', expr)
        expr_v1 = re.sub('[)][(]', ')*(', expr_sp)
        return expr_v1


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
            if entry.is_file() and entry.name.endswith('.pkl'):
                bending_names.append(entry.name)
    if not bending_names:
        return None  # handles the case that a test has no pkl file and must be skipped
    return bending_names[-1]


def plot_from_pickle(beamBendingPkl):
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


def create_csv(csvPath):
    """
    Creates a new csv file inside the test directory and writes a header in the file.
    If a csv already exists then it is removed and recreated.
    """
    if os.path.exists(csvPath):
        os.remove(csvPath)

    # write fitness data headers to a .csv file
    with open(csvPath, 'a') as csvfile:
        fieldsnames = ['binary', 'fitness', 'generations', 'solution']
        w = csv.DictWriter(csvfile, dialect='excel', fieldnames=fieldsnames)
        w.writeheader()

def main():
    """ main """
    print()  # blank line to make terminal more legible
    testPath = "/uufs/chpc.utah.edu/common/home/u1008557/tests/bnd_study/"
    csvPath = '/uufs/chpc.utah.edu/common/home/u1008557/tests/bnd_study/results.csv'
    create_csv(csvPath)

    # arrays containg fitness values for each test containing a certain hyperparameter
    pop0, pop1, stack0, stack1, dif0, dif1, cross0, cross1, mut0, mut1 = [], [], [], [], [], [], [], [], [], []

    binaries = create_binaries()
    for binary in binaries:
        binaryPath = testPath + binary + '/'
        os.chdir(binaryPath)

        beamBendingPkl = get_pkl_input()
        if beamBendingPkl is None:  # handles missing .pkl file
            print('pkl file missing from ' + os.getcwd())
            continue
        plot_from_pickle(beamBendingPkl)  # comment out when troubleshooting. Plotting takes a long time

        # simplify equation
        archipelago = load_parallel_archipelago_from_file(beamBendingPkl)
        best_ind = archipelago.get_best_individual()
        polynomial = str(Simplification(str(best_ind)).result)
        polynomial = polynomial.replace('X_0', 'x')
        # polynomial = str(best_ind) # use if polynomial is broken

        # write test results to the csv
        with open(csvPath, 'a') as csvfile:
            fieldNames = ['binary', 'fitness', 'generations', 'solution']
            w = csv.DictWriter(csvfile, dialect='excel', fieldnames=fieldNames)
            w.writerow({'binary': binary, 'fitness': best_ind.fitness,
                        'generations': archipelago.generational_age, 'solution': polynomial})

        # sort fitness into their parameter arrays
        pop, stack, dif, cross, mut = binary[:]
        pop, stack, dif, cross, mut = int(pop), int(stack), int(dif), int(cross), int(mut)
        fit = '{:.3e}'.format(best_ind.fitness)
        if pop:
            pop1.append(fit)
        elif not pop:
            pop0.append(fit)
        if stack:
            stack1.append(fit)
        elif not stack:
            stack0.append(fit)
        if dif:
            dif1.append(fit)
        elif not dif:
            dif0.append(fit)
        if cross:
            cross1.append(fit)
        elif not cross:
            cross0.append(fit)
        if mut:
            mut1.append(fit)
        elif not mut:
            mut0.append(fit)

    # write param arrays to a csv
    csv_param_path = '/uufs/chpc.utah.edu/common/home/u1008557/tests/bnd_study/param_fit.csv'
    if os.path.exists(csv_param_path):
        os.remove(csv_param_path)
    """
    pop_size = [64, 128]
    stack_size = [40, 50]
    differential_weight = [0.1, 0.4]
    crossover_rate = [0.4, 0.6]
    mutation_rate = [0.8, 1.0]
    """
    # write fitness data headers to a .csv file
    with open(csv_param_path, 'a') as csv_param:
        fieldsnames = ['pop 64', 'pop 128', 'stack 40', 'stack 50', 'dif 0.1', 'dif 0.4',
                       'cross 0.4', 'cross 0.6', 'mut 0.8', 'mut 1.0']
        w = csv.DictWriter(csv_param, dialect='excel', fieldnames=fieldsnames)
        w.writeheader()

        for i in range(len(pop0)):  # write param arrays to csv
            w.writerow({'pop 64': pop0[i], 'pop 128': pop1[i],
                        'stack 40': stack0[i], 'stack 50': stack1[i],
                        'dif 0.1': dif0[i], 'dif 0.4': dif1[i],
                        'cross 0.4': cross0[i], 'cross 0.6': cross1[i],
                        'mut 0.8': mut0[i], 'mut 1.0': mut1[i]})

main()
