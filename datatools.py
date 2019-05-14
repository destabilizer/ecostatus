'''
Tools for handle different devices with different data
'''

from dataprocessing import postprocess


class DataHandlerStack:
    def __init__(self):
        self.sourcelist = []
        self.dhstack = []
        #self.dbpath = dbpath
        self.w = False
        self.db = None
        self.sourcedb = None

    #def createDB(self):
    #    self.db.create(str(int(time.time())))

    def loadSourceDB(self, db):
        self.sourcedb = db
        for cn in self.sourcedb.list_collection_names():
            if cn not in self.sourcelist:
                self.sourcelist.append(cn)
        
    def loadDB(self, db):
        self.db = db
        for s in self.sourcelist:
            self.db.updateCollection(s)
            dh = DataHandler(db, s)
            self.dhstack.append(dh)

    def database(self):
        return self.db

    def registerSource(self, sourcename):
        if sourcename in self.sourcelist:
            print("Source is already registered")
        else:
            self._newSource(sourcename)
        
    def _newSource(self, sourcename):
        self.sourcelist.append(sourcename)
        dh = DataHandler(self.db, sourcename)
        self.dhstack.append(dh)
        self.sourcedb.updateCollection(sourcename)
        self.sourcedb.getCollection(sourcename).insertData({"source": sourcename})

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
        print("DataStack get the data from source", s)
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

    def getCollection(self):
        return self.db.getCollection(self.source)

    def _updateCollection(self):
        self.db.updateCollection(self.source)
    
    def getSource(self):
        return self.source

    def enableWriting(self):
        self._updateCollection()
        self.w = True

    def disableWriting(self):
        self.w = False

    def isWritable(self):
        return self.w
    
    def insertData(self, jsondata):
        postprocess(jsondata)
        self.lastdata = jsondata
        i = -1
        if self.isWritable():
            i = self.getCollection().insertData(jsondata)
        return i

    def lastData(self):
        return self.lastdata


class IncorrectSourceError(Exception):
    pass
