#!/usr/bin/python

#from http.server import BaseHTTPRequestHandler, HTTPServer

from flask import Flask
from flask.json import jsonify

import json
import time

from datatools import DataHandlerStack, IncorrectSourceError
from dbtools import MongoClientWrapper, CollectionNotCreatedError


app = Flask("EcoStatus")
server = None


def initserver(port=8080, mongo_address="127.0.0.1", mongo_port=27017):
    global server
    if server: raise ServerInitializationError
    server = EcoStatusServer(port, EcoStatusHandler)
    server.initMongoClient(mongo_address, mongo_port)
    server.initDataStack()
    return server


class EcoStatusServer:
    def __init__(self, port, handler_class):
        self.port = port
        #self.handler_class = handler_class
        #self.httpd = HTTPServer(('', self.port), self.handler_class)
        self.ds = None
        self.db = None
        self.mongo_client = None

    def initMongoClient(self, mongo_address, mongo_port):
        self.mongo_client = MongoClientWrapper()
        self.mongo_client.connect(mongo_address, mongo_port)

    def initDataStack(self):
        if not self.mongo_client:
            raise ServerInitializationError
        self.ds = DataHandlerStack()
        self.ds.loadSourceDB(self.mongo_client.source_db())

    def create_db(self, name):
        self.db = self.mongo_client.create_db(name)
        self.ds.loadDB(self.db)
        return name
        
    def create_db_with_timestamp(self):
        ts = time.gmtime()
        hts = time.strftime("ts%Y-%m-%d_%H:%M:%S", ts)
        return self.create_db(hts)
    
    def connectDataStack(self, dhs):
        self.ds = dhs

    def datastack(self):
        return self.ds

    def register_device(self, source):
        self.datastack().registerSource(source)

    def database(self):
        return self.db

    def enable_db_writing(self):
        self.datastack().enableWriting()

    def disable_db_writing(self):
        self.datastack().disableWriting()

    def run(self):
        app.run(port=self.port)

    def get_data(self, jsondata):
        self.datastack().insertData(jsondata)

    def last_data(self):
        ld = dict()
        ld["current"] = self.datastack().lastdata()
        ld["db"] = self.database().lastdata()
        return ld

    #def serve_forever(self):
    #    print('Starting http server...')
    #    self.httpd.serve_forever()
        

## API part

@app.route('/api/data', methods=['GET', 'POST'])
def api_data():
    if request.method == 'POST':
        try:
            jsondata = request.get_json(force=True, silent=True, cache=False)
            source = jsondata["source"]
            server.get_data(jsondata)
        except KeyError:
            raise WronJson("Wrong data json")
        except IncorrectSourceError:
            raise IncorrectSource("Source " + source + "does not exist!")
    elif request.method == "GET":
        jsondata = server.last_data()
        return jsonify(jsondata)

@app.route('/api/control', method=['GET', 'POST'])
def api_control():
    if request.method == 'POST':
        jsonreq = request.get_json(force=True, silent=True, cache=False)
        try:
            action = jsonreq["action"]
            if action == "enable_db_writing":
                server.enable_db_writing()
                return "DB writing enabled"
            elif action == "disable_db_writing":
                server.disable_db_writing()
                return "DB writing disabled"
            elif action == "new_database_with_timestamp":
                name = server.create_db_with_timestamp()
                return "Created database " + name
            elif action == "new_database":
                name = jsondata["database_name"]
                server.create_db(name)
                return "Created database " + name
            elif action == "register_device":
                source = jsondata["source"]
                r = server.register_device(source)
                if r == 0:
                    return "Device is already registered"
                elif r == 1:
                    return "Registered device " + source
            else:
                raise IncorrectAction("Action " + action + "does not exist!") 
        except KeyError:
            raise WrongJson("Wrong control json")
        except IncorrectAction:
            print("Action is incorrect")
            self.send_response(422)
    elif request.method == "GET":
        cs = server.control_status()
        return jsonjify(cs)
    
## Pages
    
@app.route('/')
def index():
    pass

@app.route('/control')
def control_panel():
    pass

## Error handler
@app.errorhandler(ServerError)
def handle_server_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


class ServerInitializationError(Exception):
    pass

class ServerError(Exception):
    status_code=400
    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class WrongJson(ServerError):
    status_code=422
    
class IncorrectAction(ServerError):
    status_code=422

class IncorrectSource(ServerError, IncorrectSourceError):
    status_code=422
