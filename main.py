from flask import Flask, request, render_template, Blueprint, jsonify
import draw
import pdb
import random
import tour
import display
from datetime import datetime

app = Flask(__name__, template_folder = './static')
drawFunc = draw.draw()

views = Blueprint('view_routes', __name__)
@views.route("/display")
def home():
    return render_template('main.html')

app.register_blueprint(views)

lp = tour.Tour()

data = Blueprint('data_routes', __name__)
@data.route("/run/tourset/<param>")
def getTour(param):
	delta = float(param[:3])
	num = int(param[3:])
	drawFunc.reset(str(delta))
	iteration = 0
	max = 279
	random.seed()
	i = random.randint(1, max)
	while iteration < num and iteration < max:
		i = (i + 1)%max
		file = 'data/tourset' + str(i) + '.csv'
		traj = 'data/trajectory/xytraj' + str(i) + '.csv'
		if(drawFunc.new(file, traj, delta)):
			if(drawFunc.run(i, delta)):
				iteration += 1
	return jsonify(drawFunc.getData())
@data.route("/run/OD", methods=['POST'])
def getOD():
	param = request.json
	if not (param['sFile'] or param['lFile']) or param['zFile']:
		param['sFile'] = 'sample.csv'
		param['lFile'] = 'manhattan_locations.csv'
		param['zFile'] = 'manhattan_zones.csv'
	start = None
	end = None
	st = "00:00"
	et = "23:59"
	if (param['startDate']):
		start = datetime.strptime(param['startDate'], '%Y-%m-%d')
	if (param['endDate']):
		end = datetime.strptime(param['endDate'], '%Y-%m-%d')
	if (param['startTime']):
		st = param['startTime']
	if (param['endTime']):
		et = param['endTime']
	dates = (start, end)
	times = (st, et)
	lp.new('data/'+param['sFile'], 'data/'+param['lFile'], 'data/'+param['zFile'])
	return jsonify(display.assignTour(lp.run(dates, times, param['maxK'], param['delta'], limit=param['num'])))

@data.route("/run/OD/<name>", methods=["POST"])
def uploadFile(name):
	if request.method == 'POST':
		request.files[name].save('data/'+name+'.csv')
		return "SUCCESSFUL UPLOAD"
	return "ERROR IN UPLOAD"

@data.route("/get/supplydemand", methods=['GET'])
def getProb():
	return jsonify(display.formatProb(lp.getProb()))

@data.route("/get/distance", methods=['GET'])
def getDistance():
	return jsonify()

@data.route("/map")
def getStops():
	return jsonify(drawFunc.getTrajectory())

app.register_blueprint(data)

if __name__ == "__main__":
    app.run()