from flask import Flask, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
import os
import json

app = Flask('API')
app.config['JSON_SORT_KEYS'] = False  # Prevent sort data and keys
api = Api(app)
os.environ['FLASK_ENV']="development"
# Remove log requests in the terminal
# log = logging.getLogger('werkzeug')
# log.disabled = True

DATA = {}
# DATA = json.load(open('Data/data_eve.json', 'r'))
DATA = json.load(open('Data/data_energy.json', 'r'))

def start_api_server():
    app.run(debug=True, host='0.0.0.0', port=None)
    # app.run()

# http://localhost:5000/api/probe
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
                for id in ids:
                    if id in list(item['id'] for item in DATA):
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
                            for property in item:
                                item[property] = item_req[property]
            elif 'id' in DATA[0]:
                ids = list(item['id'] for item in req)
                for id in ids:
                    if id not in list(item['id'] for item in DATA):
                        abort(404)
                for item in DATA:
                    for item_req in req:
                        if item_req['id'] == item['id']:
                            for property in item:
                                item[property] = item_req[property]
            else:
                abort(500)
        else:
            abort(404)
    except KeyError:
        abort(500)

    return jsonify(req), 201

# http://localhost:5000/api/probe -X DELETE
@app.route('/api/probe', methods=['DELETE'])
def delete():
    # Clear all data
    if len(DATA) > 0:
        DATA.clear()
    else:
        abort(404)

    return '', 204

# curl http://localhost:5000/api/probe/1
@app.route('/api/probe/<id>', methods=['GET'])
def get_id(id):

    # Create an empty list for our results
    results = []

    # Loop through the data and match results that fit the requested ID.
    # Abort if there is no ID in JSON data
    try:
        if len(DATA) > 0:
            if 'id' in DATA[0]:
                for item in DATA:
                    if item['id'] == int(id):
                        results.append(item)
            elif 'uuid' in DATA[0]:
                for item in DATA:
                    if item['uuid'] == id:
                        results.append(item)
            if not results:
                abort(404)
    except KeyError:
        abort(500)

    return jsonify(results)

# curl -X PUT -H "Content-Type: application/json" -d @Data/data_energy.json http://localhost:5000/api/probe/1
@app.route('/api/probe/<id>', methods=['PUT'])
def put_id(id):
    # Force JSON to avoid conflicts
    req = request.get_json(force=True)

    try:
        # ID path must match ID from data request
        if 'id' in req[0] and len(id) == 1:
            if int(id) != req[0]['id']:
                abort(404)
        elif 'uuid' in req[0]:
            if str(id) != req[0]['uuid']:
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
                if str(id) not in list(item['uuid'] for item in DATA):
                    abort(404)
                for item in DATA:
                    for item_req in req:
                        if item_req['uuid'] == item['uuid']:
                            for property in item:
                                item[property] = item_req[property]
            elif 'id' in DATA[0]:
                if int(id) not in list(item['id'] for item in DATA):
                    abort(404)
                for item in DATA:
                    for item_req in req:
                        if item_req['id'] == item['id']:
                            for property in item:
                                item[property] = item_req[property]
            else:
                abort(500)
        # If no local data, use POST request to create new instance
        else:
            abort(404)

    except KeyError:
        abort(500)

    return jsonify(req), 201

# http://localhost:5000/api/probe/1 -X DELETE
@app.route('/api/probe/<id>', methods=['DELETE'])
def delete_id(id):

    # Create an empty list for our results
    results = []

    if len(DATA) > 0:
        if 'id' in DATA[0]:
            for item in DATA:
                if item['id'] == int(id):
                    DATA.remove(item)
                    results.append(item)
        if 'uuid' in DATA[0]:
            for item in DATA:
                if item['uuid'] == id:
                    DATA.remove(item)
                    results.append(item)
    if not results:
        abort(404)

    return '', 204

start_api_server()