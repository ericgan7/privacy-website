import lp 
import csv
from cvxopt import matrix
import distance
from datetime import datetime, timedelta
from numpy import random

distance_from_file = True

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

	#Verifies that the date is within parameter's range
		#If there is no provided range, then it always returns true
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

	#Verifies that the time is within parameter's range
		#If there is no provided range, then it always returns true
	def checkTime(self, times, t):
		if times[0] and times[1]:
			return t >= times[0] and t <= times[1]
		elif times[0]:
			return t >= times[0]
		elif times[1]:
			return t <= times[1]
		else:
			return True

	#Compiles data from files.
		#Gets the latitude, longitude of all locations
		#Gets the probability of each location appearing.
		#Currently the locations are divided by zone
	def getData(self, limit, times):
		num_o = 0
		num_d = 0
		if not limit or limit <= 0:
			limit = 10
		#gets the zones data - may not be used in the future?
		for count, row in enumerate(self.zreader):
			self.zones[count] = set()
			for z in row:
				self.zones[count].add(z)
		#gets longitude latitude data
		for row in self.lreader:
			if row['location_id'] not in self.locations:
				self.locations[row['location_id']] = (row['latitude'] +', '+ row['longitude'])
		#gets supply demand probabilities
		t = self.getSupplyDemand(times)
		p = list(self.zones)
		#generates OD pairs, limit is the number of tours generated
		for i in range(limit):
			#random.choice selects one of the options based on probability
			z = random.choice(p, p = self.zoneProb)
			x = random.choice(list(self.supply[z]), p = self.supplyProb[z])
			y = random.choice(list(self.demand[z]), p = self.demandProb[z])
			#records id and location if it is a new id.
			if (x not in self.origins):
				self.origins[x] = len(self.origins)
				self.originLoc.append(self.locations[x])
			if (y not in self.destinations):
				self.destinations[y] = len(self.destinations)
				self.destinationLoc.append(self.locations[y])
			#od pairs we will use as initial od pairs
			self.data.append((x,y))
		return t

	#Gets the probability of each location appearing, based on the zone they are in.
	def getSupplyDemand(self, times):
		total = 0
		t = 0
		for i in range(len(self.zones)):
			self.supply[i] = {}
			self.demand[i] = {}
		for row in self.sreader:
			#check within datetime range
			if self.checkDate(row['timestamp'][:10]) and self.checkTime(times, row['timestamp'][11:]):
				if t == 0:
					date = datetime.strptime(row['timestamp'], self.dateFormat + ' ' + self.timeFormat)
					t = datetime(datetime.now().year + 1, date.month, date.day, date.hour, date.minute)
				#valid location
				if row['origin_id'] in self.locations and row['destination_id'] in self.locations:
					total += 2
					ozone = 0
					dzone = 0
					#records all possible zones for probabilities
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
		#enumerates probabilites
		for z in self.zones:
			self.demandProb[z] = []
			self.supplyProb[z] = []
			for s in self.supply[z].values():
				self.supplyProb[z].append(float(s)/sum(self.supply[z].values()))
			for s in self.demand[z].values():
				self.demandProb[z].append(float(s)/sum(self.demand[z].values()))
			self.zoneProb.append(float(sum(self.supply[z].values())+sum(self.demand[z].values()))/total)
		return t

	#Gets the distance matrix between each od
		#Has an option of getting distance from a file
			#Improves runtime if i does not have to query google due to query quota.
	def formatData(self, dept, parameters):
		if (len(self.origins) > 25 or len(self.destinations) > 25):
			print("Too Many stops to calculate")
		self.matrix = matrix(0., (len(self.origins), len(self.destinations)))
		self.lmatrix = matrix(0., self.matrix.size)
		#try to read distance from file. Otherwise, query google api
		if distance_from_file:
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
							y = self.destinations[dk]
							self.lmatrix[x, y] = OD_distances[(ok, dk)]
				except KeyError:
					self.getDistance(dept)
			except FileNotFoundError:
				self.getDistance(dept)
		else:
			self.getDistance(dept)
		#creates original matrix and weighted link cost matrix based on zone.
		self.weightedlmatrix = self.lmatrix
		for index, (o, d) in enumerate(self.data):
			x = self.origins[o]
			y = self.destinations[d]
			self.matrix[x,y] += 1
			for group in self.zones:
				if y in self.zones[group]:
					self.weightedlmatrix[index] *= parameters[group]
					break;

	#Gets distances from google distance matrix api
	def getDistance(self, dept):
		self.lmatrix = distance.getDistanceMatrix(self.originLoc, self.destinationLoc, dept)
		#distance.storeResult('distances.csv', self.lmatrix, self.origins, self.destinations)

	#Uses cvxopt solver to run the filter.
	def runDiffusion(self, maxK, delta):
		print(self.lmatrix)
		self.solver.new(self.matrix, self.lmatrix, self.weightedlmatrix, len(self.origins), len(self.destinations))
		self.solver.run(maxK, delta)
		return self.solver.getResults(self.origins, self.destinations, self.originLoc, self.destinationLoc)

	#Return the probability of all the possible stops - for graphing purposes.
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
		return (sup, sprob, dem, dprob)
"""
t = Tour()
t.new('data/sample.csv', 'data/manhattan_locations.csv', 'data/manhattan_zones.csv')
data = t.run((None, None),(None, None), 4, 150, limit = 5)
import display
x = display.formatProb(t.getProb())
print(x)
"""		
