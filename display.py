from cvxopt import matrix
import random

def assignTour(data):
	random.seed()
	index = random.random()
	total = 0;
	for dataSet in data:
		total += dataSet[1]
		if total >= index:
			print(dataSet[0])
			return dataSet[0]
