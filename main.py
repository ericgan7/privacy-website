from flask import Flask, request, render_template, Blueprint, jsonify
import draw
import pdb
import random
import tour
import display

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
@data.route("/run/OD", methods=['GET'])
def getOD():
	import pdb; pdb.set_trace()
	delta = float(param[:3])
	num = int(param[3:])
	lp = tour.Tour()
	sfile = 'sample.csv'
	lfile = 'location.csv'
	lp.new(sfile, lfile)
	return jsonify(display.assignTour(lp.run("2017-01-01", num, delta, limit=10)))
@data.route("/run/OD/<name>", methods=["POST"])
def uploadSFile(name):
	if request.method == 'POST':
		request.files[name].save(name+'.csv')
		return "SUCCESSFUL UPLOAD"
	return "ERROR IN UPLOAD"

@data.route("/map")
def getStops():
	return jsonify(drawFunc.getTrajectory())

app.register_blueprint(data)

if __name__ == "__main__":
    app.run()