import lp 
import csv
from cvxopt import matrix
import distance
from datetime import datetime, timedelta
from numpy import random

class Tour(object):
	def __init__(self):
		self.solver = lp.ODFilter()
		self.file = None
		self.sfile = None
		self.sreader = None
		self.lreader = None
		self.matrix = None
		self.lmatrix = None
		self.origins = {}
		self.destinations = {}
		self.locations = {}
		self.originLoc = []
		self.destinationLoc	= []
		self.data = []
		self.timeFormat = "%H:%M:%S"
		self.dateFormat = "%Y-%m-%d"
		self.supplyProb = []
		self.date = ''

	def new(self, stopName, locationName):
		self.origins = {}
		self.destinations = {}
		self.originLoc = []
		self.destinationLoc = []
		self.data = []
		self.matrix = None
		self.lmatrix = None
		self.sfile = open(stopName, 'r', newline ='')
		self.lfile = open(locationName, 'r', newline = '')
		self.sreader = csv.DictReader(self.sfile, delimiter = ',')
		self.lreader = csv.DictReader(self.lfile, delimiter = ',')
		self.supplyProb
		self.date = ''

	def run(self, date, maxK, delta, limit = 0):
		self.date = date
		dept = self.getData(limit)
		self.formatData(int(dept.timestamp()))
		return self.runDiffusion(maxK, delta)

	def check(self, date):
		date = (datetime.strptime(date, self.dateFormat))
		if (self.date[0] and self.date[1]):
			return date >= self.date[0] and date <= self.date[1]
		elif (self.date[0]):
			return date >= self.date[0]
		elif (self.date[1]):
			return date <= self.date[1]
		else:
			return True

	def getData(self, limit):
		num_o = 0
		num_d = 0
		unlimitedResults = True
		if limit and limit > 0:
			unlimitedResults = False
		else:
			limit = 2
		for row in self.lreader:
			try:
				if row['location_id'] not in self.locations:
					self.locations[row['location_id']] = (row['latitude'] +','+ row['longitude'])
			except KeyError:
				import pdb; pdb.set_trace()
		supply = {}
		total = 0
		t = 0
		for row in self.sreader:
			if self.check(row['timestamp'][:10]):
				if t == 0:
					t = datetime.strptime(row['timestamp'][:10], self.dateFormat)	
				if unlimitedResults:
					limit += 1
				if len(self.data) < limit:
					if (row['destination_id'] not in self.origins) and row['destination_id'] in self.locations and (row['origin_id'] not in self.destinations) and row['origin_id'] in self.locations:
						self.origins[row['destination_id']] = num_o
						self.originLoc.append(self.locations[row['destination_id']])
						supply[row['destination_id']] = 1
						num_o += 1
						self.destinations[row['origin_id']] = num_d
						self.destinationLoc.append(self.locations[row['origin_id']])
						num_d += 1
						self.data.append(row)
						total += 1
				if (row['origin_id'] in self.destinations and row['destination_id'] in self.origins):
					supply[row['destination_id']] += 1
					total += 1
		for i, s in enumerate(supply.values()):
			self.supplyProb.append(float(s)/total)
		return t

	def formatData(self, dept):
		if (len(self.origins) > 100 or len(self.destinations) > 100):
			print("Too Many stops to calculate")
		self.matrix = matrix(0., (len(self.origins), len(self.destinations)))
		self.lmatrix = matrix(0., self.matrix.size)
		try:
			distanceFile = open('distances.csv', 'r', newline = '')
			reader = csv.reader(distanceFile, delimiter = ',')
			for i, row in enumerate(reader):
				if i == 0:
					continue
				for j, data in enumerate(row):
					if j == 0: 
						continue
				if (i < self.lmatrix.size[0] and j < self.lmatrix.size[1]):
					try:
						self.lmatrix[i-1,j-1] = float(data)
					except:
						import pdb; pdb.set_trace()
		except FileNotFoundError:
			self.lmatrix = distance.getDistanceMatrix(self.originLoc, self.destinationLoc, dept)
			distance.storeResult('distances.csv', self.lmatrix, self.origins, self.destinations)
		supply = [int(x) for x in range(len(self.supplyProb))]
		for row in self.data:
			#idle relocation - coming from the last drop off points to new pickup points
			y = self.destinations[row['origin_id']]
			possible_x = random.choice(supply, size = 3, p = self.supplyProb)
			x = possible_x[0]
			#item is converting numpy int to native int.
			current_distance = self.lmatrix[x.item(),y]
			for i in possible_x:
				if self.lmatrix[x.item(),y] < current_distance:
					current_distance = self.lmatrix[x.item(),y]
					x = i
			#perhaps should sample multiple places and pick the closest
			self.matrix[x.item(), y] += 1.

	def runDiffusion(self, maxK, delta):
		print(self.lmatrix)
		self.solver.new(self.matrix, self.lmatrix, len(self.origins), len(self.destinations))
		self.solver.run(maxK, delta)
		return self.solver.getResults(self.originLoc, self.destinationLoc)
"""
t = Tour()
t.new('sample.csv', 'location.csv')
print(t.run('2017-01-01', 4, 100, limit = 10, time = '00:00:00'))
		"""	
				
