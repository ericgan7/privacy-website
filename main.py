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
	if not (param['sFile'] and ['param.lFile']):
		param['sFile'] = 'sample.csv'
		param['lFile'] = 'location.csv'
	start = None
	end = None
	if (param['startDate']):
		start = datetime.strptime(param['startDate'], '%Y-%m-%d')
	if (param['endDate']):
		end = datetime.strptime(param['endDate'], '%Y-%m-%d')
	dates = (start, end)
	lp = tour.Tour()
	lp.new('data/'+param['sFile'], 'data/'+param['lFile'])
	return jsonify(display.assignTour(lp.run(dates, param['maxK'], param['delta'], limit=param['num'])))
@data.route("/run/OD/<name>", methods=["POST"])
def uploadFile(name):
	if request.method == 'POST':
		request.files[name].save('data/'+name+'.csv')
		return "SUCCESSFUL UPLOAD"
	return "ERROR IN UPLOAD"

@data.route("/map")
def getStops():
	return jsonify(drawFunc.getTrajectory())

app.register_blueprint(data)

if __name__ == "__main__":
    app.run()