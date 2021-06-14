# REST API server

## Introduction



## Installation

### Development environment

#### Clone the repository
```bash
git clone https://github.com/Kaiser-14/probe-video-analysis
cd /rest-api-server/
```

#### Setup virtual environment (skip to install locally)
* **Linux/Mac**
```bash
python3 -m venv venv
source /venv/bin/activate
```

* **Windows**
```bash
\venv\Scripts\activate
```

#### Install dependencies
```bash
pip3 install -r requirements.txt
```

## Execution

There are many options to execute the program, check help manual.

```bash
python3 server.py
```

To leave the process in background
```bash
nohup /usr/bin/python3 server.py &
```

### Debug mode
Server will reload itself on code changes
```bash
python3 server.py -d
```

### Specific data (examples located in folder Data)
* **EVE**
```bash
python3 server.py -j eve
```

* **Energy**
```bash
python3 server.py -j energy
```

### Help
```bash
python3 server.py -j [JSON] -d -n [NAME] -p [PORT]
```

## Documentation
Examples of how to use the REST API

### Get all data
#### Request
`GET /api/probe`

    curl -i -H 'Content-Type: application/json' http://localhost:5000/api/probe

#### Success Response

    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 176
    Server: Werkzeug/1.0.1 Python/3.8.5
    Date: Fri, 11 Jun 2021 07:58:35 GMT


    [{'uuid':'89:81:70:2a:f4:c9','value':{'blockiness':'2.1','spatial_activity':'12.1','block_loss':'3.2','blur':'3.2','temporal_activity':'3.2'},'timestamp':'1616587589.073796'}]
    
#### Sample call
* **Python**


    requests.get('http://localhost:5000/api/probe', headers={'Content-type': 'application/json'})


### Create new data
#### Request
`POST /api/probe`

    curl -i -X POST -H 'Content-Type: application/json' -d @Data/data_eve.json http://localhost:5000/api/probe

#### Success Response

    HTTP/1.0 201 CREATED
    Content-Type: application/json
    Content-Length: 176
    Server: Werkzeug/1.0.1 Python/3.8.5
    Date: Fri, 11 Jun 2021 08:08:20 GMT
    
    [{"uuid":"89:81:70:2a:f4:c9","value":{"blockiness":"2.1","spatial_activity":"12.1","block_loss":"3.2","blur":"3.2","temporal_activity":"3.2"},"timestamp":"1616587589.073796"}]

#### Error Response

* **Code:** 409 CONFLICT <br />
**Content:** `A conflict happened while processing the request. Check if your data was previously created.`
 
OR

* **Code:** 500 INTERNAL SERVER ERROR <br />
**Content:** `The server encountered an internal error and was unable to complete your request. The properties of the request data must be the same as on the server.`
    
#### Sample call
* **Python**


    requests.post('http://localhost:5000/api/probe', json=DATA, headers={'Content-type': 'application/json'})


### Update data
`PUT /api/probe`

    curl -i -X PUT -H 'Content-Type: application/json' -d @Data/data_eve.json http://localhost:5000/api/probe

#### Success Response

    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 176
    Server: Werkzeug/1.0.1 Python/3.8.5
    Date: Fri, 11 Jun 2021 08:08:20 GMT
    
    [{"uuid":"89:81:70:2a:f4:c9","value":{"blockiness":"2.1","spatial_activity":"12.1","block_loss":"3.2","blur":"3.2","temporal_activity":"3.2"},"timestamp":"1616587589.073796"}]

#### Error Response

* **Code:** 400 BAD REQUEST <br />
**Content:** `The browser (or proxy) sent a request that this server could not understand. Your data request length should match data in the server.`
 
OR

* **Code:** 409 CONFLICT <br />
**Content:** `A conflict happened while processing the request. Check if your data was previously created.`
 
OR

* **Code:** 500 INTERNAL SERVER ERROR <br />
**Content:** `The server encountered an internal error and was unable to complete your request. The properties of the request data must be the same as on the server.`
    
#### Sample call
* **Python**
    

    requests.put('http://localhost:5000/api/probe', json=DATA, headers={'Content-type': 'application/json'})


### Delete everything
`DELETE /api/probe`

    curl -i -X DELETE -H 'Content-Type: application/json' http://localhost:5000/api/probe

#### Success Response

    HTTP/1.0 204 NO CONTENT
    Content-Type: text/html; charset=utf-8
    Server: Werkzeug/1.0.1 Python/3.8.5
    Date: Fri, 11 Jun 2021 08:01:14 GMT

#### Error Response

* **Code:** 409 CONFLICT <br />
**Content:** `A conflict happened while processing the request. There is no data to delete on the server.`
    
#### Sample call
* **Python**
    

    requests.delete('http://localhost:5000/api/probe', headers={'Content-type': 'application/json'})


### Get specific item by ID
`GET /api/probe/<item_id>`

    curl -i -H 'Content-Type: application/json' http://localhost:5000/api/probe/89:81:70:2a:f4:c9

#### Success Response

    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 176
    Server: Werkzeug/1.0.1 Python/3.8.5
    Date: Fri, 11 Jun 2021 07:58:35 GMT

    [{'uuid':'89:81:70:2a:f4:c9','value':{'blockiness':'2.1','spatial_activity':'12.1','block_loss':'3.2','blur':'3.2','temporal_activity':'3.2'},'timestamp':'1616587589.073796'}]
    
#### Sample call
* **Python**
    

    requests.get('http://localhost:5000/api/probe/89:81:70:2a:f4:c9', headers={'Content-type': 'application/json'})


### Update specific item by ID
`PUT /api/probe/<item_id>`

    curl -i -X PUT -H 'Content-Type: application/json' -d @Data/data_eve.json http://localhost:5000/api/probe/89:81:70:2a:f4:c9

#### Success Response

    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 176
    Server: Werkzeug/1.0.1 Python/3.8.5
    Date: Fri, 11 Jun 2021 08:08:20 GMT
    
    [{"uuid":"89:81:70:2a:f4:c9","value":{"blockiness":"2.1","spatial_activity":"12.1","block_loss":"3.2","blur":"3.2","temporal_activity":"3.2"},"timestamp":"1616587589.073796"}]

#### Error Response

* **Code:** 400 BAD REQUEST <br />
**Content:** `The browser (or proxy) sent a request that this server could not understand.`
 
OR

* **Code:** 409 CONFLICT <br />
**Content:** `A conflict happened while processing the request. Requested URL ID does not correspond with provided ID in data request.`

OR

* **Code:** 409 CONFLICT <br />
**Content:** `A conflict happened while processing the request. Check if your data was previously created.`
     
OR

* **Code:** 500 INTERNAL SERVER ERROR <br />
**Content:** `The server encountered an internal error and was unable to complete your request. The properties of the request data must be the same as on the server.`
    
#### Sample call
* **Python**
    

    requests.put('http://localhost:5000/api/probe', json=DATA, headers={'Content-type': 'application/json'})


### Remove specific item by ID
`DELETE /api/probe/<item_id>`

    curl -i -X DELETE -H 'Content-Type: application/json' http://localhost:5000/api/probe/89:81:70:2a:f4:c9

#### Success Response

    HTTP/1.0 204 NO CONTENT
    Content-Type: text/html; charset=utf-8
    Server: Werkzeug/1.0.1 Python/3.8.5
    Date: Fri, 11 Jun 2021 08:01:14 GMT

#### Error Response

* **Code:** 409 CONFLICT <br />
**Content:** `A conflict happened while processing the request. There is no data to delete on the server.`
    
#### Sample call
* **Python**
    

    requests.delete('http://localhost:5000/api/probe/89:81:70:2a:f4:c9', headers={'Content-type': 'application/json'})


### Shutdown the server
`GET/PROBE /api/probe/shutdown`

    curl -i -H 'Content-Type: application/json' http://localhost:5000/api/probe/shutdown

OR

    curl -i -X POST -H 'Content-Type: application/json' http://localhost:5000/api/probe/shutdown

#### Success Response

    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 176
    Server: Werkzeug/1.0.1 Python/3.8.5
    Date: Fri, 11 Jun 2021 07:58:35 GMT

    Shutting down the server...
    
#### Sample call
* **Python**


    requests.get('http://localhost:5000/api/probe/89:81:70:2a:f4:c9', headers={'Content-type': 'application/json'})