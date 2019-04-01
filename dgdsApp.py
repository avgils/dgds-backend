# LIBS
import json

# FLASK
from flask import Flask
from flask import request, jsonify
from flask_cors import CORS

# PROJECT
from dgdsPiServiceDDL import *

# FLASK app
application = Flask(__name__)
CORS(application)

# PiSerivceUrl-DDL: for now hardcoded. Config file? Services?
PISERVICE_URL = 'http://pl-tc012.xtr.deltares.nl:8080/FewsWebServices/rest/digitaledelta/2.0'

# Hostname URL: Also hard-coded for now, sorry
HOSTNAME_URL = 'http://localhost:5000'

# JSON input to dict
def readInputJSON():
	# Inputs
	jsonData = request.get_json()
	return jsonData

# dict to JSON
def prepareOutputJSON(content, status):
	return jsonify(content), status

# Application root - /
@application.route('/', methods=['GET'])
def slash():	
	content = {'error': 'nothing to see here, perhaps looking for /datasets, /timeseries or /locations?'}
	return prepareOutputJSON(content, 200)

# Query locations - /locations
@application.route('/locations', methods=['GET'])
def locations():
	# Read input [JSON] - Parameters can be either JSON or url parameters. Not both. [adapted for the paging]
	inputJson = readInputJSON()
	inputUrl = request.args.to_dict(flat=True)

	# Query PiService
	pi = PiServiceDDL(PISERVICE_URL, HOSTNAME_URL)
	if inputUrl != {}:
		content = pi.getLocations(inputUrl)
	else:
		content = pi.getLocations(inputJson)

	return prepareOutputJSON(content, 200)

# Dummy locations - /dummylocations
@application.route('/dummylocations', methods=['GET'])
def dummyLocations():
	# Return dummy file contents
	with open('./dummyData/dummyLocations.json') as f:
		content = json.load(f)
	return prepareOutputJSON(content, 200)

# Time-series query - /tseries
@application.route('/timeseries', methods=['GET'])
def tseries():
	# Read input [JSON] - Parameters can be either JSON or url parameters. Not both.
	inputJson = readInputJSON()
	inputUrl = request.args.to_dict(flat=True)

	# Query PiService
	pi = PiServiceDDL(PISERVICE_URL, HOSTNAME_URL)
	if inputUrl != {}:
		content = pi.getTimeSeries(inputUrl)
	else:
		content = pi.getTimeSeries(inputJson)

	return prepareOutputJSON(content, 200)

# Dummy timeseries - /dummytimeseries
@application.route('/dummytimeseries', methods=['GET'])
def dummyTimeseries():
	# Return dummy file contents
	with open('./dummyData/dummyTseries.json') as f:
		content = json.load(f)
	return prepareOutputJSON(content, 200)

# Main
if __name__ == "__main__":
	application.run(host='0.0.0.0', debug=True)    