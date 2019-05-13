#import pymongo
import time

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
        self.collections_to_update = []

    def loadDB(self, db):
        self.db = db
        for cn in self.db.list_collection_names():
            self._updateCollection(cn)
        self._updateCollections()
    
    def create(self, name):
        self.db = FakeDB() # TODO mongo initialization
        self._updateCollections()

    def create_with_timestamp(self):
        self.create(str(int(time.time())))
    
    def _createCollection(self, collection_name):
        self.db.createCollection(collection_name)
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
        print("Inserting data into the database...")
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
        print(jsondata)
