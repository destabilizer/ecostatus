#!/usr/bin/python

from http.server import BaseHTTPRequestHandler, HTTPServer
import json

from datatools import DataHandlerStack, IncorrectSourceError
from dbtools import CollectionNotCreatedError

_is_server_initializated = False


def initserver(port=8080):
    global _is_server_initializated
    if _is_server_initializated: raise ServerInitializationError
    _is_server_initializated = True
    s = EcoStatusServer(port, EcoStatusHandler)
    EcoStatusHandler.server = s
    return s


class EcoStatusServer:
    def __init__(self, port, handler_class):
        self.port = port
        self.handler_class = handler_class
        self.httpd = HTTPServer(('', self.port), self.handler_class)

    def initDataStack(self):
        self.ds = DataHandlerStack()

    def createDB(self):
        self.datastack().createDB()
    
    def connectDataStack(self, dhs):
        self.ds = dhs

    def datastack(self):
        return self.ds

    def database(self):
        return self.datastack().database()

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
            print(post_body)
            print(post_body.decode("utf-8"))
            jsondata = json.loads(post_body.decode("utf-8"))
            print(jsondata)
        except:
            print("POST with incorrect json")
            self.send_response(400)
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
                    self.wfile.write(b"Writing enables")
                    print("Writing in DB enabled")
                elif jsondata["action"] == "disable_db_writing":
                    EcoStatusHandler.server.datastack().disableWriting()
                    self._set_headers()
                    self.wfile.write(b"Writing disabled")
                    print("Writing in DB disabled")
                elif jsondata["action"] == "new_database_with_timestamp":
                    ...
                elif jsondata["action"] == "new_database":
                    ...
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
        #except Exception as e:
        #    print("POST with unknown error")
        #    self.send_response(400)


class ServerError(Exception):
    pass

class ServerInitializationError(ServerError):
    pass

class IncorrectAction(ServerError):
    pass
