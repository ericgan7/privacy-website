from cvxopt import matrix
import random
#This file is used to formatting the data for JSON format.

#Generates a random number and samples the data
def assignTour(data):
	random.seed()
	index = random.random()
	total = 0;
	for dataSet in data:
		total += dataSet[2]
		if total >= index:
			print("probability total " + str(total) + ', ' + str(index))
			return (dataSet[0], dataSet[1])

#Format the probability into JSON format
def formatProb(data):
	supply = data[0]
	supProb = data[1]
	demand = data[2]
	demProb = data[3]
	sup = {}
	dem = {}
	for index, key in enumerate(supply):
		sup[key] = supProb[index]
	for index, key in enumerate(demand):
		dem[key] = demProb[index]
	return {'origin': sup, 'destination': dem}
