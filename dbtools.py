#import pymongo


class DBWrapper:
    _default_mongo_address = 'localhost'
    _default_mongo_port = 27017
    
    def __init__(self, db=None, address='', port=0):
        self.db = db
        self.collections = []
        if db: self.loadDB(db)
        if not address:
            self.address = DBWrapper._default_mongo_address
        else:
            self.address = address
        if not port:
            self.port = DBWrapper._default_mongo_port
        else:
            self.port = port

    def loadDB(self, db):
        self.db = db
        for cn in self.db.list_collection_names():
            self.addCollection(collection_name)
    
    def create(self, name):
        self.db = FakeDB() # TODO mongo initialization
    
    def createCollection(self, collection_name):
        self.db.createCollection(collection_name)
        w = DBCollectionWrapper(self.db[collection_name], collection_name)
        self.collections.append(w)
        return w

    def addCollection(self, collection_name):
        cw = DBCollectionWrapper(self.db[collection_name], collection_name)
        self.collections.append(cw)
        return cw

    def list_collection_names(self):
        return self.db.list_collection_names()

    def updateCollection(self, collection_name):
        if collection_name not in self.list_collection_names():
            return self.createCollection(collection_name)
        else:
            return self.addCollection(collection_name)

    def lastData(self):
        return [cw.lastData() for cw in self.collections]

    
class DBCollectionWrapper:
    def __init__(self, collection, collection_name):
        self.collection = collection
        self.collection_name = collection_name
        self.lastdata = None

    def name(self):
        return self.collection_name

    def insertData(self, jsondata):
        #maybe some operations with jsondata
        self.lastdata = jsondata
        print("Inserting data into the database...")
        return self.collection.insert_one(jsondata)

    def lastData(self):
        return self.lastdata


# This is for testing

class FakeDB:
    def __init__(self):
        self.collections = []
        print("FakeDB created")

    def list_collection_names(self):
        return self.collections

    def createCollection(self, collection_name):
        self.collections.append(collection_name)
        print("Added collection " + collection_name)

    def __getitem__(self, cn):
        return FakeCollection()
    
class FakeCollection:
    def insert_one(self, jsondata):
        print(jsondata)
