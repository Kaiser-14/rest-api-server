from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource
import logging
import json
import os

app = Flask('API')
api = Api(app)
os.environ['FLASK_ENV']="development"
# Remove log requests in the terminal
# log = logging.getLogger('werkzeug')
# log.disabled = True

DATA = {}
file = open('Data/data_energy.json', 'r')
DATA = json.load(file)

def abort_request(item_id):
    if item_id not in DATA:
        abort(404, message="{} doesn't exist".format(item_id))


def start_api_server():
    app.run(debug=True, host='0.0.0.0', port=None)


# API Reference
class Data(Resource):
    # curl http://localhost:5000/api/probe/sensor1
    def get(self, item_id):
        abort_request(item_id)
        return DATA[item_id]

    # curl http://localhost:5000/api/probe/sensor1 -X DELETE
    def delete(self, item_id):
        abort_request(item_id)
        for property in DATA[item_id]:
            DATA[item_id][property] = ""
        return '', 204

    # curl http://localhost:5000/api/probe/sensor1 -d "voltage=1.1&current=2.2&active_power=3.2&power_factor=4.1" -X PUT
    def put(self, item_id):
        abort_request(item_id)
        for property in DATA[item_id]:
            DATA[item_id][property] = request.form[property]
        return DATA[item_id], 201


class DataList(Resource):
    # curl http://localhost:5000/api/probe
    def get(self):
        return DATA

    # curl http://localhost:5000/api/probe -X DELETE
    def delete(self):
        for item_id in DATA:
            for property in DATA[item_id]:
                DATA[item_id][property] = ""
        return '', 204

    # curl http://localhost:5000/api/probe -d "voltage=1.1&current=2.2&active_power=3.2&power_factor=4.1" -X PUT
    def put(self):
        for item_id in DATA:
            # DATA[item_id] = request.form[item_id]
            for property in item_id:
                DATA[item_id][property] = request.form[property]
        return DATA, 201

    # curl http://localhost:5000/api/probe -d "voltage=1.1&current=2.2&active_power=3.2&power_factor=4.1" -X POST
    def post(self):
        item_id_new = list(DATA.keys())[0][:-1] + '%d' % (len(DATA) + 1)
        DATA[item_id_new] = {}
        for item_id in DATA:
            for property in DATA[item_id]:
                DATA[item_id_new][property] = request.form[property]
            break
        return DATA[item_id_new], 201


# API routing resources
api.add_resource(Data, '/api/probe/<string:item_id>')
api.add_resource(DataList, '/api/probe')

start_api_server()
