from cvxopt import matrix, spmatrix, solvers, log, spdiag
import numpy
import math
import csv
recordParam = False

class ODFilter(object):
	def __init__(self, matrix = None, lmatrix = None, origins = None, destinations = None):
		solvers.options['maxiters'] = 200
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
		self.wlmatrix = None

	def new(self, matrix, lmatrix, wlmatrix, origins, destinations):
		self.o = origins
		self.d = destinations
		self.tours = []
		self.original = matrix
		self.linkCost = lmatrix
		self.wlmatrix = wlmatrix
		self.cost = None
		self.validTours = []
		self.invalidTours = []
		self.k = 1
		self.tours.append(matrix)
		self.validTours.append(matrix)
		self.diffusion = None
		if (recordParam):
			self.record(self.original, 'Original', '', self.o, self.d)

	# Remakes original matrix so that it is distance optimized
		#uses a weighted matrix based on zone
		#for pure distance, switch cost matrix from self.wlmatrix to self.lmatrix
	def optimizeLinkCost(self):
		costMat = matrix(self.wlmatrix, (len(self.original), 1))
		variableConstraints = matrix(-1.*numpy.eye(len(costMat)))
		equalityConstraints = matrix(0., (self.o + self.d, len(costMat)))
		variableSolutions = matrix(numpy.zeros(len(costMat)), (len(costMat), 1))
		equalitySolutions = matrix(0., (self.o + self.d, 1))
		#sets the equailty constraints to the correct sum in row / column
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
		self.original = matrix(solvers.lp(costMat, variableConstraints, variableSolutions,
				equalityConstraints, equalitySolutions, solver='glpk')['x'], (self.o, self.d))
		print(self.original)

	#sp1 - generate new tours
	def generateTours(self, max):
		while self.k < max:
			costMat = matrix(0., (len(self.original), 1))
			#cost matrix aggregating in U and K everystep
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
			#sets the equailty constraints to the correct sum in row / columm
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
			#glpk solver to get new od matrix. cvxopt for documentation
			newMat = solvers.lp(costMat, variableConstraints, variableSolutions,
				equalityConstraints, equalitySolutions, solver='glpk')
			if (recordParam):
				self.record(newMat['x'], 'generated_OD', self.k, self.o, self.d)
			self.validTours.append(newMat['x'])
			self.tours.append(newMat['x'])
			self.k += 1

	#not implemented
	def inverseOptimization(self):
		objectiveVariables = matrix(1.0, (2, len(self.original)))
		inequalityConstraints = matrix()

	#sp2 - assigns diffusion based on principle of maximum entropy
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
		#uses a nonlinear convex problem solver. see cvxopt for documentation
		sol = solvers.cp(self.F, G=inequalityConstraints, h=inequalitySolutions,
			A=equalityConstraints, b=equalitySolutions)
		if(recordParam):
			self.record(sol['x'], 'Diffusion', '', sol['x'].size[0], sol['x'].size[1])
		total = 0.
		for i in range(self.k):
			total += sol['x'][i]*inequalityConstraints[1,i]
		#max iterations of 200 does not always find optimal solution. 
		#Unsure if I should increase the cap or just use unoptimal solution.
		print(sol['x'])
		print(self.linkCost)
		return sol['x']

	#objective function used for diffusion
		#f is the function (x ln x)
		#df is the first derivative
		#H is the second derivative
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

	#running the filter
	def run(self, maxK, delta):
		#set original matrix
		self.optimizeLinkCost()
		maxIter = 10
		iterations = 0
		while (iterations < maxIter):
			print("ITERATION " + str(iterations))
			iterations += 1
			#generate set of k tours
			self.generateTours(maxK)
			#assign diffuction
			sol = self.checkEntropy(delta)
			#if all are greater than zero, accept the solution
			if (min(sol) > 0):
				self.diffusion = sol
				return
			removal = []
			#else continue to generate tours
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
	#returns (stop ids, locations, and probability) in format:
		#	((originid, destinationid), (origin latlng, destination latlng), probability)
	def getResults(self, ori, dest, oLoc, dLoc):
		if (self.diffusion):
			results = []
			for index in range(len(self.validTours)):
				mat = matrix(self.validTours[index], (self.o, self.d))
				k = 0
				locations = {}
				ids = {}
				for i, x in enumerate(ori):
					for j, y in enumerate(dest):
						if(mat[i, j] > 0.):
							try: 
								locations[k] = (oLoc[ori[x]], dLoc[dest[y]])
								ids[k] = (x, y)
								k += 1
							except:
								import pdb; pdb.set_trace()
				results.append((ids, locations, self.diffusion[index]))
			return results
		return None

		#records results for testing
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


