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
		
Running:
	In command line, navigate to folder.
	Run main.py using python.
		This will start a local server. Crtl+ c will interrupt it and shut it down
	Go to 'localhost:5000/display' to open the website.
	
Querying:
	The destination/origin files, latitude/longitude files, and zone files are optional. If used, it will likely require all 3 files be uploaded or there may be data discrepencies. If none are provided it will use a defualt sample that I used to test.
	Time range and date range are also optional. You may define a start, end, or both and they will limit the data it searches. Timezone may effect the distance calculations is makes
	Num tours, maxK, and delta are required. If num is left blank, it will generate 10 od pairs by default. max K must provided, with maxK >= 0. Delta must be provided, with >= 0. A too small delta will result in an unoptimal solution, which has unpredictable results.
	Search button will switch it to map view and start compiling data. It may take a few seconds to display it on the map due to Google's query quota and amount of data. 

Iteraction:
	The side bar has a dropdown menu that holds all the od pairs, called tour (1 - num tours).
	Hovering over each tour will highlight the tour on the map. It will also make a marker appear on the the destination, which usually does not appear to minimize clutter.
	You can uncheck the the tour boxes to make them disappear from the map, will also removes the row from the table.
	There is a switch that will toggle all the tours on or off.
	The table page lists all the latitude logitude coordinates of each stop of the od pairs.
	The statistics page lists all the possible stop locations that could be generated, since the data is synthetic.
	


	


