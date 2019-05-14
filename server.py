#!/usr/bin/python

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time

from datatools import DataHandlerStack, IncorrectSourceError
from dbtools import MongoClientWrapper, CollectionNotCreatedError

_is_server_initializated = False


def initserver(port=8080, mongo_address="127.0.0.1", mongo_port=27017):
    global _is_server_initializated
    if _is_server_initializated: raise ServerInitializationError
    _is_server_initializated = True
    s = EcoStatusServer(port, EcoStatusHandler)
    s.initMongoClient(mongo_address, mongo_port)
    s.initDataStack()
    EcoStatusHandler.server = s
    return s


class EcoStatusServer:
    def __init__(self, port, handler_class):
        self.port = port
        self.handler_class = handler_class
        self.httpd = HTTPServer(('', self.port), self.handler_class)
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
        
    def create_db_with_timestamp(self):
        ts = time.gmtime()
        hts = time.strftime("ts%Y-%m-%d_%H:%M:%S", ts)
        self.create_db(hts)
    
    def connectDataStack(self, dhs):
        self.ds = dhs

    def datastack(self):
        return self.ds

    def database(self):
        return self.db

    def serve_forever(self):
        print('Starting http server...')
        self.httpd.serve_forever()
        
        
class EcoStatusHandler(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()
    
    def do_GET(self):
        self._set_headers()
        dsld = EcoStatusHandler.server.datastack().lastData()
        dbld = EcoStatusHandler.server.database().lastData()
        self.wfile.write(b"<html><body>")
        self.wfile.write(b"<p>")
        self.wfile.write(bytes(str(dsld), "utf-8"))
        self.wfile.write(b"</p>")
        self.wfile.write(b"<p>")
        self.wfile.write(bytes(str(dbld), "utf-8"))
        self.wfile.write(b"</p>")
        self.wfile.write(b"</body></html>")

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        try:
            print("POST:", post_body.decode("utf-8"))
            jsondata = json.loads(post_body.decode("utf-8"))
        except:
            print("POST with incorrect json")
            self.send_response(400)
            self.wfile.write(b"Incorrect json")
            return
        try:
            if jsondata["type"] == "data":
                EcoStatusHandler.server.datastack().insertData(jsondata)
                self._set_headers()
                self.wfile.write(b"POST with data")
                print("Caught some data")
            elif jsondata["type"] == "control":
                if jsondata["action"] == "enable_db_writing":
                    EcoStatusHandler.server.datastack().enableWriting()
                    self._set_headers()
                    self.wfile.write(b"Writing enabled")
                    print("Writing in DB enabled")
                elif jsondata["action"] == "disable_db_writing":
                    EcoStatusHandler.server.datastack().disableWriting()
                    self._set_headers()
                    self.wfile.write(b"Writing disabled")
                    print("Writing in DB disabled")
                elif jsondata["action"] == "new_database_with_timestamp":
                    EcoStatusHandler.server.database().create_with_timestamp()
                    self._set_headers()
                elif jsondata["action"] == "new_database":
                    dbname = jsondata["dbname"]
                    EcoStatusHandler.server.database().create(dbname)
                    self._set_headers()
                elif jsondata["action"] == "register_source":
                    source = jsondata["source"]
                    EcoStatusHandler.server.datastack().registerSource(source)
                    self._set_headers()
                else:
                    raise IncorrectAction
        except KeyError:
            print("POST with bad json")
            self.send_response(422)
        except IncorrectSourceError:
            print("Source is not registered on server")
            self.send_response(422) # Actually it means that source is not registered, http code ???
        except CollectionNotCreatedError:
            print("Collection was not created!")
            self.send_response(422)
        except IncorrectAction:
            print("Action is incorrect")
            self.send_response(422)
        #except SourceIsAlreadyRegisteredError:
        #    print("Source is already registered")
        #    self.send_response(200)
        #    self.wfile.write(b"Source is already registered")
        #except Exception as e:
        #    print("POST with unknown error")
        #    self.send_response(400)


class ServerError(Exception):
    pass

class ServerInitializationError(ServerError):
    pass

class IncorrectAction(ServerError):
    pass
