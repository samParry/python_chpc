# -*- coding: utf-8 -*-
""" @author: Sam Parry, Erick Solum """

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
#from problems.beam_bending import analytic_solution
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
import sys

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

	if beamBendingPkl is None:	# handles missing .pkl file
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
		fieldsnames = ['Training Data', 'success', 'fitness', 'generations', 'solution']
		w = csv.DictWriter(csvfile, dialect='excel', fieldnames=fieldsnames)
		w.writeheader()

def main():
	""" main """
	print()  # blank line to make terminal more legible
	testPath = "/uufs/chpc.utah.edu/common/home/u1008557/tests/bnd_tdata/"
	csvPath = '/uufs/chpc.utah.edu/common/home/u1008557/tests/bnd_tdata/results.csv'
	create_csv(csvPath)
	t_list = ['t2', 't4', 't4-new', 't8', 't16', 't32', 't64']
	for t in t_list:
		tPath = testPath + t + '/'
		os.chdir(tPath)

		for i in range(1,31):
			trialPath = '{0}trial{1}/'.format(tPath,i)
			os.chdir(trialPath)

			beamBendingPkl = get_pkl_input()
			if beamBendingPkl is None:	# handles missing .pkl file
				print('pkl file missing from ' + os.getcwd())
				continue
			#plot_from_pickle(beamBendingPkl)  # comment out when troubleshooting. Plotting takes a long time

			# simplify equation
			try:
				archipelago = load_parallel_archipelago_from_file(beamBendingPkl)
			except:
				print('change your python path to:\nPYTHONPATH=/uufs/chpc.utah.edu/common/home/u6019587/bin/bingo_fork:/uufs/chpc.utah.edu/common/home/u6019587/src/bingo_diffeq_tf')
				sys.exit()
			best_ind = archipelago.get_best_individual()
			polynomial = str(Simplification(str(best_ind)).result)
			polynomial = polynomial.replace('X_0', 'x')
			# polynomial = str(best_ind) # use if polynomial is broken

			# Did the test converge and exit successfully?
			success = 'False'
			if float(best_ind.fitness) <= 1e-7:
				success = 'True'

			# write test results to the csv
			with open(csvPath, 'a') as csvfile:
				fieldNames = ['Training Data', 'success', 'fitness', 'generations', 'solution']
				w = csv.DictWriter(csvfile, dialect='excel', fieldnames=fieldNames)
				w.writerow({'Training Data': t[1:], 'success': success, 'fitness': best_ind.fitness,
							'generations': archipelago.generational_age, 'solution': polynomial})

main()
