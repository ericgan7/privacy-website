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
		self.zfile = None
		self.sreader = None
		self.lreader = None
		self.zreader = None
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
		self.supplyProb = {}
		self.demandProb = {}
		self.date = ''
		self.supply = {}
		self.demand = {}
		self.zoneProb = []
		self.zones = {}
		self.weightedlmatrix = None

	def new(self, stopName, locationName, zoneName):
		self.origins = {}
		self.destinations = {}
		self.originLoc = []
		self.destinationLoc = []
		self.data = []
		self.sfile = open(stopName, 'r', newline ='')
		self.lfile = open(locationName, 'r', newline = '')
		self.zfile = open(zoneName, 'r', newline = '')
		self.sreader = csv.DictReader(self.sfile, delimiter = ',')
		self.lreader = csv.DictReader(self.lfile, delimiter = ',')
		self.zreader = csv.reader(self.zfile, delimiter = ',')
		self.supplyProb = {}
		self.demandProb = {}
		self.date = ''
		self.supply = {}
		self.demand = {}
		self.zones = {}
		self.zoneProb = []

	def run(self, date, times, maxK, delta, limit):
		self.date = date
		dept = self.getData(limit, times)
		parameters = self.zoneProb
		self.formatData(int(dept.timestamp()), parameters)
		return self.runDiffusion(maxK, delta)

	def checkDate(self, date):
		date = (datetime.strptime(date, self.dateFormat))
		if (self.date[0] and self.date[1]):
			return date >= self.date[0] and date <= self.date[1]
		elif (self.date[0]):
			return date >= self.date[0]
		elif (self.date[1]):
			return date <= self.date[1]
		else:
			return True
	def checkTime(self, times, t):
		if times[0] and times[1]:
			return t >= times[0] and t <= times[1]
		elif times[0]:
			return t >= times[0]
		elif times[1]:
			return t <= times[1]
		else:
			return True

	def getData(self, limit, times):
		num_o = 0
		num_d = 0
		if not limit or limit <= 0:
			limit = 10
		for count, row in enumerate(self.zreader):
			self.zones[count] = set()
			for z in row:
				self.zones[count].add(z)
		for row in self.lreader:
			if row['location_id'] not in self.locations:
				self.locations[row['location_id']] = (row['latitude'] +','+ row['longitude'])
		t = self.getSupplyDemand(times)
		p = list(self.zones)
		for i in range(limit):
			z = random.choice(p, p = self.zoneProb)
			x = random.choice(list(self.supply[z]), p = self.supplyProb[z])
			y = random.choice(list(self.demand[z]), p = self.demandProb[z])
			if (x not in self.origins):
				self.origins[x] = len(self.origins)
				self.originLoc.append(self.locations[x])
			if (y not in self.destinations):
				self.destinations[y] = len(self.destinations)
				self.destinationLoc.append(self.locations[y])
			self.data.append((x,y))
		return t

	def getSupplyDemand(self, times):
		total = 0
		t = 0
		for i in range(len(self.zones)):
			self.supply[i] = {}
			self.demand[i] = {}
		for row in self.sreader:
			if self.checkDate(row['timestamp'][:10]) and self.checkTime(times, row['timestamp'][11:]):
				if t == 0:
					date = datetime.strptime(row['timestamp'], self.dateFormat + ' ' + self.timeFormat)
					t = datetime(datetime.now().year + 1, date.month, date.day, date.hour, date.minute)
				if row['origin_id'] in self.locations and row['destination_id'] in self.locations:
					total += 2
					ozone = 0
					dzone = 0
					for group in self.zones:
						if row['origin_id'] in self.zones[group]:
							ozone = group
						if row['destination_id'] in self.zones[group]:
							dzone = group
					if (row['destination_id'] not in self.supply[dzone]):
						self.supply[dzone][row['destination_id']] = 1
					else:
						self.supply[dzone][row['destination_id']] += 1
					if (row['origin_id'] not in self.demand[ozone]):
						self.demand[ozone][row['origin_id']] = 1
					else:
						self.demand[ozone][row['origin_id']] += 1
		for z in self.zones:
			self.demandProb[z] = []
			self.supplyProb[z] = []
			for s in self.supply[z].values():
				self.supplyProb[z].append(float(s)/sum(self.supply[z].values()))
			for s in self.demand[z].values():
				self.demandProb[z].append(float(s)/sum(self.demand[z].values()))
			self.zoneProb.append(float(sum(self.supply[z].values())+sum(self.demand[z].values()))/total)
		return t

	def formatData(self, dept, parameters):
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
		self.weightedlmatrix = self.lmatrix
		distance.storeResult('distances.csv', self.lmatrix, self.origins, self.destinations)
		for index, (o, d) in enumerate(self.data):
			x = self.origins[o]
			y = self.destinations[d]
			self.matrix[x,y] += 1
			for group in self.zones:
				if y in self.zones[group]:
					self.weightedlmatrix[index] *= parameters[group]
					break;

	def runDiffusion(self, maxK, delta):
		print(self.lmatrix)
		self.solver.new(self.matrix, self.lmatrix, self.weightedlmatrix, len(self.origins), len(self.destinations))
		self.solver.run(maxK, delta)
		return self.solver.getResults(self.origins, self.destinations, self.originLoc, self.destinationLoc)

	def getProb(self):
		sprob = []
		sup = []
		dprob = []
		dem = []
		for z in self.zones:
			for s in list(self.supply[z]):
				sup.append(s)
			for s in self.supplyProb[z]:
				sprob.append(s * self.zoneProb[z])
			for d in list(self.demand[z]):
				dem.append(d)
			for d in self.demandProb[z]:
				dprob.append(d * self.zoneProb[z])
		import pdb; pdb.set_trace()
		return (sup, sprob, dem, dprob)

t = Tour()
t.new('data/sample.csv', 'data/manhattan_locations.csv', 'data/manhattan_zones.csv')
data = t.run((None, None),(None, None), 4, 150, limit = 5)
import display
x = display.formatProb(t.getProb())
print(x)
				
