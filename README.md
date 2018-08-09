# privacy-website

Uses python, javascript, and html

Required python packages:
	Flask
		Used to host a server, handles requests
	cvxopt
		Used for matrix representations and linear programming solvers
	numpy
		Used for random choice generation
Html Packages (CDN):
	Chart.js
	Google Api
	ajax
	jquery
	bootstrap
	bootstrap-toggle

Project Description:
	Implement a data filter for origin, destination pairs following the methodology of the paper.

Project Implementation
	Consists of several steps:
		Data aggregation. Using NYC taxi data, we generate supply and demand probabilities and sample serveral tours.

		Optimization. Since the initial suppply demand is random, we solve a shorest paths problem on the OD pairs, modified by their zone weights, to make sure the original tour set makes sense
		SP1 - Tour generation. Formula described in paper, implemented in python.
		Inverse Optimization Filter - not implemented.
		SP2 - Diffusion assignment based on maximizing entropy.
			Loops if necessary
		Sample the data for output data.

	Website is used to query and visual the data:
		Flask is used to host a local server to fetch and post urls.
		

	


