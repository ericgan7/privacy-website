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
		self.timeFormat = "%H:%M"
		self.dateFormat = "%Y-%m-%d"
		self.supplyProb = []
		self.demandProb = []
		self.date = ''
		self.supply = {}
		self.demand = {}

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
		self.supplyProb = []
		self.demandProb = []
		self.date = ''
		self.supply = {}
		self.demand = {}

	def run(self, date, maxK, delta, limit):
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
		if not limit or limit <= 0:
			limit = 10
		for row in self.lreader:
			try:
				if row['location_id'] not in self.locations:
					self.locations[row['location_id']] = (row['latitude'] +','+ row['longitude'])
			except KeyError:
				import pdb; pdb.set_trace()
		t = self.getSupplyDemand()
		s = list(self.supply)
		d = list(self.demand)
		for i in range(limit):
			x = random.choice(s, p = self.supplyProb)
			y = random.choice(d, p = self.demandProb)
			if (x not in self.origins):
				self.origins[x] = len(self.origins)
				self.originLoc.append(self.locations[x])
			if (y not in self.destinations):
				self.destinations[y] = len(self.destinations)
				self.destinationLoc.append(self.locations[y])
			self.data.append((x,y))
		return t

	def getSupplyDemand(self):
		total = 0
		t = 0
		for row in self.sreader:
			if self.check(row['timestamp'][:10]):
				if t == 0:
					date = datetime.strptime(row['timestamp'], self.dateFormat + ' ' + self.timeFormat)
					t = datetime(datetime.now().year + 1, date.month, date.day, date.hour, date.minute)
				if row['origin_id'] in self.locations and row['destination_id'] in self.locations:
					total += 1
					if (row['destination_id'] not in self.supply):
						self.supply[row['destination_id']] = 1
					else:
						self.supply[row['destination_id']] += 1
					if (row['origin_id'] not in self.demand):
						self.demand[row['origin_id']] = 1
					else:
						self.demand[row['origin_id']] += 1
		for i, s in enumerate(self.demand.values()):
			self.demandProb.append(float(s)/total)
		for i, s in enumerate(self.supply.values()):
			self.supplyProb.append(float(s)/total)
		return t

	def formatData(self, dept):
		if (len(self.origins) > 100 or len(self.destinations) > 100):
			print("Too Many stops to calculate")
		self.matrix = matrix(0., (len(self.origins), len(self.destinations)))
		self.lmatrix = matrix(0., self.matrix.size)
		"""
		try:
			distanceFile = open('distances.csv', 'r', newline = '')
			reader = csv.DictReader(distanceFile, delimiter = ',')
			OD_distances = {}
			i = 0
			for row in reader:
				if i == 0:
					i += 1
					continue
				for j, key in enumerate(row):
					if j == 0: 
						row_origin = row[key]
						continue
					OD_distances[(row_origin, key)] = row[key]
			try:
				for ok in self.origins:
					x = self.origins[ok]
					for dk in self.destinations:
						y = self.origins[dk]
						self.lmatrix[x, y] = OD_distances[(ok, dk)]
			except KeyError:
				import pdb; pdb.set_trace()
		except FileNotFoundError:
			"""
		self.lmatrix = distance.getDistanceMatrix(self.originLoc, self.destinationLoc, dept)
		distance.storeResult('distances.csv', self.lmatrix, self.origins, self.destinations)
		for o, d in self.data:
			x = self.origins[o]
			y = self.destinations[d]
			self.matrix[x,y] += 1

	def runDiffusion(self, maxK, delta):
		print(self.lmatrix)
		self.solver.new(self.matrix, self.lmatrix, len(self.origins), len(self.destinations))
		self.solver.run(maxK, delta)
		return self.solver.getResults(self.origins, self.destinations, self.originLoc, self.destinationLoc)

	def getProb(self):
		return (self.supply, self.supplyProb, self.demand, self.demandProb)
"""
t = Tour()
t.new('data/sample.csv', 'data/location.csv')
data = t.run((None, None), 4, 150, limit = 5)
import display
x = display.formatProb(t.getProb())
print(x)
"""
				
