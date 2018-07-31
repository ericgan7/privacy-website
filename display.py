from cvxopt import matrix
import random

def assignTour(data):
	random.seed()
	index = random.random()
	total = 0;
	for dataSet in data:
		total += dataSet[2]
		if total >= index:
			print("probability total " + str(total) + ', ' + str(index))
			return (dataSet[0], dataSet[1])
