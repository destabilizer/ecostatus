from pymongo import MongoClient
import time

class MongoClientWrapper:
    def __init__(self):
        self.port = None
        self.address = None

    def connect(self, port, address):
        self.port = port
        self.address = address
        self.client = MongoClient()

    def create_db(self, name):
        return DBWrapper(db=self.client[name])

    def source_db(self):
        db = DBWrapper(self.client["registered_devices"])
        #db.updateCollection("lattepanda1") # It's for testing
        #db.updateCollection("lattepanda2")
        #db.updateCollection("testclient")
        return db
        

class DBWrapper:
    def __init__(self, db=None):
        self.db = db
        self.collections = []
        self.collections_to_update = []
        if db: self.loadDB(db)

    def loadDB(self, db):
        self.db = db
        for cn in self.db.list_collection_names():
            self._updateCollection(cn)
        self._updateCollections()
    
    def _createCollection(self, collection_name):
        self.db[collection_name]
        self._addCollection(collection_name)

    def _addCollection(self, collection_name):
        cw = DBCollectionWrapper(self.db[collection_name], collection_name)
        self.collections.append((collection_name, cw))

    def list_collection_names(self):
        return [c[0] for c in self.collections]

    def _updateCollection(self, collection_name):
        if collection_name not in self.list_collection_names():
            return self._createCollection(collection_name)

    def _updateCollections(self):
        for cn in self.collections_to_update:
            self._updateCollection(cn)
        self.collections_to_update = []
        
    def updateCollection(self, collection_name): # lazy function, can update without database
        if self.db:
            self._updateCollection(collection_name)
        else:
            self.collections_to_update.append(collection_name)
        
    def getCollection(self, collection_name):
        for c in self.collections:
            if c[0] == collection_name:
                return c[1]
        else:
            raise CollectionNotCreatedError

    def lastData(self):
        return [c[1].lastData() for c in self.collections]

    
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
        print("Inserting data into the collection", self.collection_name)
        return self.collection.insert_one(jsondata)

    def lastData(self):
        return self.lastdata


class CollectionNotCreatedError(Exception):
    pass

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
        print("FakeCollection:", jsondata)
