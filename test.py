import flask
from flask import jsonify

d = {}
d[0] = "hello"
d[1] = "world"

jsonify(d)