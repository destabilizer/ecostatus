#!/usr/bin/python

#from http.server import BaseHTTPRequestHandler, HTTPServer

from flask import Flask, request
from flask.json import jsonify

import json
import time

from datatools import DataHandlerStack, IncorrectSourceError
from dbtools import MongoClientWrapper, CollectionNotCreatedError

from pymongo.errors import ServerSelectionTimeoutError


app = Flask("EcoStatus")
app.testing = True
server = None


def initserver(port=8080, mongo_address="127.0.0.1", mongo_port=27017):
    global server
    if server: raise ServerInitializationError
    server = EcoStatusServer(port, mongo_address, mongo_port)
    return server


class EcoStatusServer:
    def __init__(self, port=None, mongo_address=None, mongo_port=None):
        self.port = port
        self.mongo_address = mongo_address
        self.mongo_port = mongo_port
        self.ds = None
        self.db = None
        self.mongo_client = None
        self.mongo_client_initialized = False
        self.db_created = False

    def addPort(self, port):
        self.port = port
  
    def addMongo(self, address, port):
        self.mongo_address = address
        self.mongo_port = port

    def initMongoClient(self):
        self.mongo_client = MongoClientWrapper()
        if not (self.mongo_address and self.mongo_port):
            raise ServerIsNotFullyInitialized("Set up Mongo params")
        try:
            self.mongo_client.connect(self.mongo_address, self.mongo_port)
            self.mongo_client.client.list_database_names()   # checking is it really connected
            self.mongo_client_initialized = True
        except ServerSelectionTimeoutError:
            print("Could not connect to Mongo server! Set it up")
            raise MongoIsNotUpError("Could not connect to Mongo")

    def mongoclient(self):
        self._update_mongo()
        return self.mongo_client

    def initDataStack(self):
        self.ds = DataHandlerStack()
        self.ds.loadSourceDB(self.mongoclient().source_db())

    def create_db(self, name):
        self.db = self.mongoclient().create_db(name)
        self.datastack().loadDB(self.db)
        return name
        
    def create_db_with_timestamp(self):
        ts = time.gmtime()
        hts = time.strftime("ts%Y-%m-%d_%H:%M:%S", ts)
        return self.create_db(hts)

    def connectDataStack(self, dhs):
        self.ds = dhs

    def _update_mongo(self):
        if not self.mongo_client_initialized:
            self.initMongoClient()

    def _update_datastack(self):
        if not self.ds:
            self.initDataStack()

    def _update_database(self):
        if not self.db:
            print("Implicitly created database")
            self.create_db_with_timestamp()

    def datastack(self):
        self._update_datastack()
        return self.ds

    def register_device(self, jsondata):
        return self.datastack().registerSource(jsondata)

    def database(self):
        self._update_database()
        return self.db
    
    def enable_db_writing(self):
        self._update_database()
        return self.datastack().enableWriting()

    def disable_db_writing(self):
        return self.datastack().disableWriting()

    def run(self):
        if not self.port:
            raise ServerIsNotFullyInitializedError("Set up server port")
        app.run(port=self.port)

    def get_data(self, jsondata):
        return self.datastack().insertData(jsondata)

    def last_data(self):
        ld = dict()
        ld["current"] = self.datastack().lastData()
        ld["db"] = self.database().lastData()
        return ld

    def control_status(self):
        cs = dict()
        cs["is_db_writing_enabled"] = self.datastack().isWritable()
        cs["current_database"] = self.database().getName()
        cs["regisitered_devices"] = self.datastack().source_list()
        cs["visible_devices"] = self.datastack().visible_sources()
        return cs

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
            id = server.get_data(jsondata)
            return jsonify({"_id": id})
        except KeyError:
            raise WrongJson("Wrong data json")
        except IncorrectSourceError:
            raise IncorrectSource("Source " + source + "does not exist!")
    elif request.method == "GET":
        jsondata = server.last_data()
        return jsonify(jsondata)

@app.route('/api/control', methods=['GET', 'POST'])
def api_control():
    if request.method == 'POST':
        jsonreq = request.get_json(force=True, silent=True, cache=False)
        try:
            action = jsonreq["action"]
            if action == "enable_db_writing":
                r = server.enable_db_writing()
                return jsonify({"changed": r})
            elif action == "disable_db_writing":
                r = server.disable_db_writing()
                return jsonify({"changed": r})
            elif action == "new_database_with_timestamp":
                name = server.create_db_with_timestamp()
                return jsonify({"database_name": name})
            elif action == "new_database":
                name = jsonreq["database_name"]
                server.create_db(name)
                return jsonify({"database_name": name})
            elif action == "register_device":
                jsondata = jsonreq.copy()
                jsondata.pop("action")
                r = server.register_device(jsondata)
                return jsonify(r)
            else:
                raise IncorrectAction("Action " + action + "does not exist!") 
        except KeyError:
            raise WrongJson("Wrong control json")
        except IncorrectAction:
            print("Action is incorrect")
            self.send_response(422)
    elif request.method == "GET":
        cs = server.control_status()
        return jsonify(cs)
    
## Pages
    
@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        api_data()
    elif request.method == 'GET':
        index()

def index():
    return str()

@app.route('/control')
def control_panel():
    pass


## Error block

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

class ServerIsNotFullyInitialized(ServerError):
    status_code=500

class MongoIsNotUpError(ServerError):
    status_code=500
    
class WrongJson(ServerError):
    status_code=422
    
class IncorrectAction(ServerError):
    status_code=422

class IncorrectSource(ServerError, IncorrectSourceError):
    status_code=422


@app.errorhandler(ServerError)
def handle_server_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

