import json, requests
from cvxopt import matrix
import csv
from math import floor
import time

base_url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
api_key = 'AIzaSyBqpLvV-_k0XAhR_RaEprhlDjorrkp-UP0'

#Gets distance matrix
def getDistanceMatrix(origin, destination, dept):
	progress = 0
	#blank matrix
	linkCost = matrix(0., (len(origin), len(destination)))
	t = time.time()
	while progress < len(origin):
		payload = {
			'origins' : origin[progress],
			'destinations' : '|'.join(destination),
			'departure_time' : dept,
			'traffic_model' : 'best_guess',
			'key' : api_key
		}
		results = requests.get(base_url, params = payload)
		if results.status_code != 200:
			print('ERROR FETCHING DISTANCES : ' + str(results.status_code))
		else:
			mat = json.loads(results.text)
			if(mat['status'] != 'OK'):
				print('QUERY ERROR')
			else:
				#Request is sucessful - adds it into distance matrix
				for i, row in enumerate(mat['rows']):
					for j, data in enumerate(row['elements']):
						try:
							linkCost[i+progress, j] = data['duration']['value']+data['duration_in_traffic']['value']
						except KeyError:
							linkCost[i+progress, j] = data['duration']['value']
				progress += 1
	print(time.time() - t)
	return linkCost

#stores the results of distance matrix
def storeResult(fileName, linkCost, originNames, destNames):
	with open(fileName, 'w', newline = '') as file:
		writer = csv.writer(file, delimiter = ',')
		num_o, num_d = linkCost.size
		row = [None]
		for i, d in enumerate(destNames):
			row.append(d)
		writer.writerow(row)
		for i, o in enumerate(originNames):
			row = [o]
			for j, d in enumerate(destNames):
				row.append(linkCost[i,j])
			writer.writerow(row)
	file.close()