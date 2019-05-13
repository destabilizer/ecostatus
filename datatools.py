'''
Tools for handle different devices with different data
'''

from dbtools import DBWrapper
from dataprocessing import postprocess


class DataHandlerStack:
    def __init__(self):
        self.sourcelist = []
        self.dhstack = []
        #self.dbpath = dbpath
        self.w = False
        self.db = DBWrapper()

    #def createDB(self):
    #    self.db.create(str(int(time.time())))

    def loadDB(self, db):
        self.db = db        
        #TODO check that it has correct collections

    def database(self):
        return self.db

    def registerSource(self):
        ...

    def newSource(self, sourcename):
        self.sourcelist.append(sourcename)
        dh = DataHandler(self.db, sourcename)
        self.dhstack.append(dh)

    def appendDataHandler(self, dh):
        dhs = dh.getSource()
        if dhs in self.sourcelist:
            raise IncorrectSourceError
        self.sourcelist.append(sourcename)
        if self.isWritable():
            dh.enableWriting()
        else:
            dh.disableWriting()
        self.dhstack.append(dh)

    def insertData(self, jsondata):
        s = jsondata["source"]
        try:
            i = self.sourcelist.index(s)
        except:
            raise IncorrectSourceError
        print("DataStack get the data with source", s)
        return self.dhstack[i].insertData(jsondata)

    def lastData(self):
        return [dh.lastData() for dh in self.dhstack]

    def enableWriting(self):
        for dh in self.dhstack:
            dh.enableWriting()
        self.w = True

    def disableWriting(self):
        for dh in self.dhstack:
            dh.disableWriting()
        self.w = False

    def isWritable(self):
        return self.w


class DataHandler:
    def __init__ (self, db, sourcename):
        self.source = sourcename
        self.lastdata = None
        self.w = False
        self.db = db
        self.collection = None
        self.collection_initialized = False

    def getCollection(self):
        return self.db.getCollection(self.source)

    def _init_collection(self):
        self.collection = self.db.updateCollection(self.source)
    
    def getSource(self):
        return self.source

    def enableWriting(self):
        self._init_collection()
        self.w = True

    def disableWriting(self):
        self.w = False

    def isWritable(self):
        return self.w
    
    def insertData(self, jsondata):
        postdata = postprocess(jsondata)
        self.lastdata = postdata
        i = -1
        if self.isWritable():
            i = self.getCollection().insertData(postdata)
        return i

    def lastData(self):
        return self.lastdata


class IncorrectSourceError(Exception):
    pass
