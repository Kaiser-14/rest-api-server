import argparse
import json
import logging
import os

from flask import Flask, request, jsonify
from flask_restful import abort, Api

parser = argparse.ArgumentParser(description='Multimedia probe analysis.')
parser.add_argument(
	'-j',
	dest='json',
	type=str,
	help='JSON template for instances in server')
parser.add_argument(
	'-d',
	dest='debug',
	const=True,
	default=False,
	nargs='?',
	help='Debug mode to restart server if any change in the code')
parser.add_argument(
	'-q',
	dest='quiet',
	const=True,
	default=False,
	nargs='?',
	help='Quiet mode to remove received request from terminal')
parser.add_argument(
	'-n',
	dest='host',
	type=str,
	default='0.0.0.0',
	help='Name of the host server')
parser.add_argument(
	'-p',
	dest='port',
	type=int,
	default=5000,
	help='Name of the host server')

args = parser.parse_args()

api_name = 'API'
DATA = {}
if args.json == 'eve':
	DATA = json.load(open('Data/data_eve.json', 'r'))
	api_name = '5G-EVE Rest API'
elif args.json == 'energy':
	DATA = json.load(open('Data/data_energy.json', 'r'))
	api_name = '5G-Energy Rest API'

# Define API
app = Flask(api_name)
app.config['JSON_SORT_KEYS'] = False  # Prevent sort data and keys
api = Api(app)
os.environ['FLASK_ENV'] = "development"

# Remove log requests in the terminal
if args.quiet:
	log = logging.getLogger('werkzeug')
	log.disabled = True


def start_api_server():
	app.run(debug=args.debug, host=args.host, port=args.port)


# curl http://localhost:5000/api/probe
@app.route('/api/probe', methods=['GET'])
def get():
	return jsonify(DATA)


# curl -X POST -H "Content-Type: application/json" -d @Data/data_eve.json http://localhost:5000/api/probe
@app.route('/api/probe', methods=['POST'])
def post():
	# Force JSON to avoid conflicts
	req = request.get_json(force=True)

	try:
		# Loop through actual data to check ID. Create new 
		# instance only if not present ID, abort otherwise
		if len(DATA) > 0:
			if 'id' in DATA[0]:
				ids = list(item['id'] for item in req)
				for id_item in ids:
					if id_item in list(item['id'] for item in DATA):
						abort(409)
				for item_req in req:
					DATA.append(item_req)
			elif 'uuid' in DATA[0]:
				uuids = list(item['uuid'] for item in req)
				for uuid in uuids:
					if uuid in list(item['uuid'] for item in DATA):
						abort(409)
				for item_req in req:
					DATA.append(item_req)
		else:
			for item in req:
				DATA.append(item)
	except KeyError:
		abort(500)

	return jsonify(req), 201


# curl -X PUT -H "Content-Type: application/json" -d @Data/data_eve.json http://localhost:5000/api/probe
@app.route('/api/probe', methods=['PUT'])
def put():
	# Force JSON to avoid conflicts
	req = request.get_json(force=True)

	try:
		# Loop through data to check ID. Abort if not
		# match every requested ID with data
		if len(DATA) > 0:
			if 'uuid' in DATA[0]:
				uuids = list(item['uuid'] for item in req)
				for uuid in uuids:
					if uuid not in list(item['uuid'] for item in DATA):
						abort(404)
				for item in DATA:
					for item_req in req:
						if item_req['uuid'] == item['uuid']:
							for property_item in item:
								item[property_item] = item_req[property_item]
			elif 'id' in DATA[0]:
				ids = list(item['id'] for item in req)
				for id_item in ids:
					if id_item not in list(item['id'] for item in DATA):
						abort(404)
				for item in DATA:
					for item_req in req:
						if item_req['id'] == item['id']:
							for property_item in item:
								item[property_item] = item_req[property_item]
			else:
				abort(500)
		else:
			abort(404)
	except KeyError:
		abort(500)

	return jsonify(req), 200


# curl http://localhost:5000/api/probe -X DELETE
@app.route('/api/probe', methods=['DELETE'])
def delete():
	# Clear all data
	if len(DATA) > 0:
		DATA.clear()
	else:
		abort(404)

	return '', 204


# curl http://localhost:5000/api/probe/1
@app.route('/api/probe/<identification>', methods=['GET'])
def get_id(identification):

	# Create an empty list for our results
	results = []

	# Loop through the data and match results that fit the requested ID.
	# Abort if there is no ID in JSON data
	try:
		if len(DATA) > 0:
			if 'id' in DATA[0]:
				for item in DATA:
					if item['id'] == int(identification):
						results.append(item)
			elif 'uuid' in DATA[0]:
				for item in DATA:
					if item['uuid'] == identification:
						results.append(item)
			if not results:
				abort(404)
	except KeyError:
		abort(500)

	return jsonify(results)


# curl -X PUT -H "Content-Type: application/json" -d @Data/data_energy.json http://localhost:5000/api/probe/1
@app.route('/api/probe/<identification>', methods=['PUT'])
def put_id(identification):
	# Force JSON to avoid conflicts
	req = request.get_json(force=True)

	try:
		# ID path must match ID from data request
		if 'id' in req[0] and len(identification) == 1:
			if int(identification) != req[0]['id']:
				abort(404)
		elif 'uuid' in req[0]:
			if str(identification) != req[0]['uuid']:
				abort(404)
		else:
			abort(500)

		# Allow only one instance, as it is individual request
		if len(req) > 1:
			abort(404)

		# Loop through data to check ID. Abort if not
		# match requested ID with any data
		if len(DATA) > 0:
			if 'uuid' in DATA[0]:
				if str(identification) not in list(item['uuid'] for item in DATA):
					abort(404)
				for item in DATA:
					for item_req in req:
						if item_req['uuid'] == item['uuid']:
							for property_item in item:
								item[property_item] = item_req[property_item]
			elif 'id' in DATA[0]:
				if int(identification) not in list(item['id'] for item in DATA):
					abort(404)
				for item in DATA:
					for item_req in req:
						if item_req['id'] == item['id']:
							for property_item in item:
								item[property_item] = item_req[property_item]
			else:
				abort(500)
		# If no local data, use POST request to create new instance
		else:
			abort(404)

	except KeyError:
		abort(500)

	return jsonify(req), 200


# curl http://localhost:5000/api/probe/1 -X DELETE
@app.route('/api/probe/<identification>', methods=['DELETE'])
def delete_id(identification):

	# Create an empty list for our results
	results = []

	if len(DATA) > 0:
		if 'id' in DATA[0]:
			for item in DATA:
				if item['id'] == int(identification):
					DATA.remove(item)
					results.append(item)
		if 'uuid' in DATA[0]:
			for item in DATA:
				if item['uuid'] == identification:
					DATA.remove(item)
					results.append(item)
	if not results:
		abort(404)

	return '', 204


if __name__ == '__main__':
	start_api_server()
