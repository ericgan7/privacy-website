from cvxopt import matrix, spmatrix, solvers, log, spdiag
import numpy
import math
import csv
recordParam = False

class ODFilter(object):
	def __init__(self, matrix = None, lmatrix = None, origins = None, destinations = None):
		solvers.options['maxiters'] = 100
		self.tours = []
		self.validTours = []
		self.invalidTours = []
		self.k = 1
		self.o = origins
		self.d = destinations
		self.cost = None
		self.linkCost = None
		self.diffusion = None
		if (matrix):
			self.original = matrix
			self.tours.append(matrix)
			self.validTours.append(matrix)
		if (lmatrix):
			self.linkCost = lmatrix

	def new(self, matrix, lmatrix, origins, destinations):
		self.o = origins
		self.d = destinations
		self.tours = []
		self.original = matrix
		self.linkCost = lmatrix
		self.cost = None
		self.validTours = []
		self.invalidTours = []
		self.k = 1
		self.tours.append(matrix)
		self.validTours.append(matrix)
		self.diffusion = None
		if (recordParam):
			self.record(self.original, 'Original', '', self.o, self.d)

	def generateTours(self, max):
		while self.k < max:
			costMat = matrix(0., (len(self.original), 1))
			for mat in self.tours:
				for index, value in enumerate(mat):
					costMat[index] += value
			self.cost = costMat
			if (recordParam):
				self.record(self.cost, 'Cost', self.k, self.o, self.d)
			variableConstraints = matrix(-1.*numpy.eye(len(costMat)))
			equalityConstraints = matrix(0., (self.o + self.d, len(costMat)))
			variableSolutions = matrix(numpy.zeros(len(costMat)), (len(costMat), 1))
			equalitySolutions = matrix(0., (self.o + self.d, 1))
			for i in range(self.d):
				temp = self.original[:, i]
				for index in range(self.o):
					equalityConstraints[i,index + self.o*i] = 1
				equalitySolutions[i] = sum(temp)
			for i in range(self.o):
				temp = self.original[i, :]
				for index in range(self.d):
					equalityConstraints[i + self.d, self.o*index + i] = 1
				equalitySolutions[self.d + i] = sum(temp)

			newMat = solvers.lp(costMat, variableConstraints, variableSolutions,
				equalityConstraints, equalitySolutions, solver='glpk')
			if (recordParam):
				self.record(newMat['x'], 'generated_OD', self.k, self.o, self.d)
			self.validTours.append(newMat['x'])
			self.tours.append(newMat['x'])
			self.k += 1

	def checkEntropy(self, delta):
		const = 0
		for index in range(len(self.cost)):
			const += self.linkCost[index]*self.original[index]

		inequalityConstraints = matrix(-1., (2 + self.k, self.k))
		inequalitySolutions = matrix(0., (2 + self.k, 1))

		for i, mat in enumerate(self.validTours):
			c = 0
			for index in range(len(self.cost)):
				c += mat[index] * self.linkCost[index]
			inequalityConstraints[0, i] = -c
			inequalityConstraints[1, i] = c
		inequalitySolutions[0, 0] = delta - const
		inequalitySolutions[1, 0] = delta + const

		equalityConstraints = matrix(1., (1, self.k))
		equalitySolutions = matrix(1., (1,1))
		sol = solvers.cp(self.F, G=inequalityConstraints, h=inequalitySolutions,
			A=equalityConstraints, b=equalitySolutions)
		if(recordParam):
			self.record(sol['x'], 'Diffusion', '', sol['x'].size[0], sol['x'].size[1])
		total = 0.
		for i in range(self.k):
			total += sol['x'][i]*inequalityConstraints[1,i]
		print(sol['x'])
		return sol['x']

	def F(self, x = None, z = None):
		if(x is None): 
			return 0, matrix(1., (len(self.validTours), 1))
		if (min(x) < 0.0):
			return None
		f = (x.T * log(x))
		Df = (1. + log(x)).T
		if (z is None):
			return f, Df
		H = spdiag(z * x**(-1))
		return f, Df, H

	def run(self, maxK, delta):
		maxIter = 10
		iterations = 0
		while (iterations < maxIter):
			print("ITERATION " + str(iterations))
			iterations += 1
			self.generateTours(maxK)
			sol = self.checkEntropy(delta)
			if (min(sol) > 0):
				self.diffusion = sol
				return
			removal = []
			for i in range(sol.size):
				if (sol[i] == 0.):
					self.invalidTours.append(self.validTours[i])
					removal.append(self.validTours[i])
			for t in removal:
				self.validTours.remove(t)
			k = len(self.validTours)
			for mat in self.invalidTours:
				if mat in self.tours:
					continue
				else:
					self.tours.append(mat)

	def getResults(self, ori, dest):
		if (self.diffusion):
			results = []
			for index in range(len(self.validTours)):
				mat = matrix(self.validTours[index], (self.o, self.d))
				k = 0
				locations = {}
				for i in range(self.o):
					row = []
					for j in range(self.d):
						if(mat[i,j] > 0.):
							k += 1
							locations[k] = (ori[i], dest[j])
				results.append((locations, self.diffusion[index]))
			return results
		return None

	def record(self, matrix, type, iteration, o, d):
		with  open(str(type)+str(iteration)+'.csv', 'w', newline = '') as file:
			writer = csv.writer(file, delimiter=',')
			for i in range(o):
				row = []
				for j in range(d):
					row.append(matrix[i*d + j])
				writer.writerow(row)
		file.close()

			

"""
start = matrix([[50,0,0],[0,0,200],[50, 150,0]])
link = matrix([[4,18,13],[17,7,13],[11,6,21]])
test = ODFilter(start, link, 3, 3)
test.run(4,900)
"""


