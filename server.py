import argparse
import json
import logging
import os

from flask import Flask, request, jsonify, abort
from flask_restful import Api

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
	'-s',
	dest='server',
	type=str,
	default='0.0.0.0',
	help='Name of the host server')
parser.add_argument(
	'-p',
	dest='port',
	type=int,
	default=5000,
	help='Host server port')

args = parser.parse_args()

api_name = 'API'
DATA = []
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
	app.run(debug=args.debug, host=args.server, port=args.port)


# curl http://localhost:5000/api/probe
@app.route('/api/probe', methods=['GET'])
def get():
	return jsonify(DATA)


# curl -X POST -H "Content-Type: application/json" -d @Data/data_eve.json http://localhost:5000/api/probe
@app.route('/api/probe', methods=['POST'])
def post():
	# Force JSON to avoid conflicts
	data_request = request.get_json(force=True)

	try:
		# Loop through actual data to check ID. Create new 
		# instance only if not present ID, abort otherwise
		if len(DATA) > 0:
			if 'id' in DATA[0]:
				ids = list(item['id'] for item in data_request)
				for id_item in ids:
					if id_item in list(item['id'] for item in DATA):
						abort(409, 'A conflict happened while processing the request. Check if your data was previously created.')
				for item_request in data_request:
					DATA.append(item_request)
			elif 'uuid' in DATA[0]:
				uuids = list(item['uuid'] for item in data_request)
				for uuid in uuids:
					if uuid in list(item['uuid'] for item in DATA):
						abort(409, 'A conflict happened while processing the request. Check if your data was previously created.')
				for item_request in data_request:
					DATA.append(item_request)
		else:
			for item in data_request:
				DATA.append(item)
	except KeyError:
		abort(500, 'The server encountered an internal error and was unable to complete your request. Verify the sending of the same information as on the server')

	return jsonify(data_request), 201


# curl -X PUT -H "Content-Type: application/json" -d @Data/data_eve.json http://localhost:5000/api/probe
@app.route('/api/probe', methods=['PUT'])
def put():
	# Force JSON to avoid conflicts
	data_request = request.get_json(force=True)

	try:
		# Loop through data to check ID. Abort if not
		# match every requested ID with data
		if len(DATA) == len(data_request):
			if 'uuid' in DATA[0]:
				uuids = list(item['uuid'] for item in data_request)
				for uuid in uuids:
					if uuid not in list(item['uuid'] for item in DATA):
						abort(409, 'A conflict happened while processing the request. Check if your data was previously created.')
				for item in DATA:
					for item_request in data_request:
						if item_request['uuid'] == item['uuid']:
							for property_item in item:
								item[property_item] = item_request[property_item]
			elif 'id' in DATA[0]:
				ids = list(item['id'] for item in data_request)
				for id_item in ids:
					if id_item not in list(item['id'] for item in DATA):
						abort(409, 'A conflict happened while processing the request. Check if your data was previously created.')
				for item in DATA:
					for item_request in data_request:
						if item_request['id'] == item['id']:
							for property_item in item:
								item[property_item] = item_request[property_item]
			else:
				abort(500, 'The server encountered an internal error and was unable to complete your request. The properties of the request data must be the same as on the server.')
		else:
			abort(400, 'The browser (or proxy) sent a request that this server could not understand. Your data request length should match data in the server.')
	except KeyError:
		abort(500, 'The server encountered an internal error and was unable to complete your request. The properties of the request data must be the same as on the server.')

	return jsonify(data_request), 200


# curl http://localhost:5000/api/probe -X DELETE
@app.route('/api/probe', methods=['DELETE'])
def delete():
	# Clear all data
	if len(DATA) > 0:
		DATA.clear()
	else:
		abort(409, 'A conflict happened while processing the request. There is no data to delete on the server.')

	return '', 204


# curl http://localhost:5000/api/probe/1
@app.route('/api/probe/<item_id>', methods=['GET'])
def get_id(item_id):
	# Create an empty list for our results
	results = []

	# Loop through the data and match results that fit the requested ID.
	# Abort if there is no ID in JSON data
	try:
		if len(DATA) > 0:
			if 'id' in DATA[0]:
				for item in DATA:
					if item['id'] == int(item_id):
						results.append(item)
			elif 'uuid' in DATA[0]:
				for item in DATA:
					if item['uuid'] == item_id:
						results.append(item)
			if not results:
				abort(404)
	except KeyError:
		abort(500, 'The server encountered an internal error and was unable to complete your request. The properties of the request data must be the same as on the server.')

	return jsonify(results)


# curl -X PUT -H "Content-Type: application/json" -d @Data/data_energy.json http://localhost:5000/api/probe/1
@app.route('/api/probe/<item_id>', methods=['PUT'])
def put_id(item_id):
	# Force JSON to avoid conflicts
	data_request = request.get_json(force=True)

	try:
		# ID path must match ID from data request
		if 'id' in data_request[0]:
			if int(item_id) != data_request[0]['id']:
				abort(409, 'A conflict happened while processing the request. Requested URL ID does not correspond with provided ID in data request.')
		elif 'uuid' in data_request[0]:
			if str(item_id) != data_request[0]['uuid']:
				abort(409, 'A conflict happened while processing the request. Requested URL ID does not correspond with provided ID in data request.')
		else:
			abort(500, 'The server encountered an internal error and was unable to complete your request. The properties of the request data must be the same as on the server.')

		# Allow only one instance, as it is individual request
		if len(data_request) > 1:
			abort(400, 'The browser (or proxy) sent a request that this server could not understand.')

		# Loop through data to check ID. Abort if not
		# match requested ID with any data
		if len(DATA) > 0:
			if 'uuid' in DATA[0]:
				if str(item_id) not in list(item['uuid'] for item in DATA):
					abort(409, 'A conflict happened while processing the request. Check if your data was previously created.')
				for item in DATA:
					for item_request in data_request:
						if item_request['uuid'] == item['uuid']:
							for property_item in item:
								item[property_item] = item_request[property_item]
			elif 'id' in DATA[0]:
				if int(item_id) not in list(item['id'] for item in DATA):
					abort(409, 'A conflict happened while processing the request. Check if your data was previously created.')
				for item in DATA:
					for item_request in data_request:
						if item_request['id'] == item['id']:
							for property_item in item:
								item[property_item] = item_request[property_item]
			else:
				abort(500, 'The server encountered an internal error and was unable to complete your request. The properties of the request data must be the same as on the server.')
		# If no local data, use POST request to create new instance
		else:
			abort(400, 'The browser (or proxy) sent a request that this server could not understand.')

	except KeyError:
		abort(500, 'The server encountered an internal error and was unable to complete your request. The properties of the request data must be the same as on the server.')

	return jsonify(data_request), 200


# curl http://localhost:5000/api/probe/1 -X DELETE
@app.route('/api/probe/<item_id>', methods=['DELETE'])
def delete_id(item_id):
	# Create an empty list for our results
	results = []

	if len(DATA) > 0:
		if 'id' in DATA[0]:
			for item in DATA:
				if item['id'] == int(item_id):
					DATA.remove(item)
					results.append(item)
		if 'uuid' in DATA[0]:
			for item in DATA:
				if item['uuid'] == item_id:
					DATA.remove(item)
					results.append(item)
	if not results:
		abort(409, 'A conflict happened while processing the request. There is no data to delete on the server.')

	return '', 204


# curl http://localhost:5000/api/probe/shutdown
@app.route('/api/probe/shutdown', methods=['GET', 'POST'])
def shutdown_server():
	shutdown = request.environ.get('werkzeug.server.shutdown')
	if shutdown is None:
		raise RuntimeError('The function is unavailable')
	else:
		shutdown()
		return 'Shutting down the server...\n'


if __name__ == '__main__':
	start_api_server()
