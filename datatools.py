'''
Tools for handle different devices with different data
'''

from dataprocessing import postprocess


class DataHandlerStack:
    def __init__(self):
        self.sourcelist = []
        self.visible = []
        self.dhstack = []
        #self.dbpath = dbpath
        self.w = False
        self.db = None
        self.sourcedb = None

    #def createDB(self):
    #    self.db.create(str(int(time.time())))

    def loadSourceDB(self, db):
        self.sourcedb = db
        for cn in self.sourcedb.db.list_collection_names():
            self.load_source(cn)
        
    def loadDB(self, db):
        self.db = db
        for dh in self.dhstack:
            dh.db = self.db
            dh._updateCollection()

    def source_list(self):
        return self.sourcelist

    def visible_sources(self):
        return self.visible
    
    def database(self):
        return self.db

    def registerSource(self, jsondata):
        sn = jsondata["source"]
        col = self.sourcedb.db[sn]
        if sn in self.sourcelist:
            col.delete_one({})
        else:
            self.sourcelist.append(sn)
            dh = DataHandler(self.db, sn)
            self.dhstack.append(dh)
        col.insert_one(jsondata)
        jsondata.pop("_id")
        if jsondata["visible"]:
            self.visible.append(sn)
        else:
            if sn in visible:
                self.visible.pop(sn)
        return jsondata

    def load_source(self, sourcename):
        if not sourcename in self.sourcelist:
            self.sourcelist.append(sourcename)
            dh = DataHandler(self.db, sourcename)
            self.dhstack.append(dh)
        sourcecol = self.sourcedb.db[sourcename]
        source_param = sourcecol.find_one()
        try:
            if source_param["visible"]:
                if not sourcename in self.visible:
                    self.visible.append(sourcename)
        except KeyError:
            pass

    #def _newSource(self, jsondata):
    #    sn = jsondata["source"]
    #    self.sourcelist.append(sn)
    #    dh = DataHandler(self.db, sn)
    #    self.dhstack.append(dh)
    #    self.sourcedb.updateCollection(sn)
    #    self.sourcedb.getCollection(sourcename).insertData(jsondata)

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
        return {dh.source:dh.lastData() for dh in self.dhstack}

    def enableWriting(self):
        if self.w == True:
            return False
        else:
            for dh in self.dhstack:
                dh.enableWriting()
            self.w = True
            return True

    def disableWriting(self):
        if self.w == False:
            return False
        else:
            for dh in self.dhstack:
                dh.disableWriting()
            self.w = False
            return True

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
        print(self.lastdata)
        if self.isWritable():
            return self.getCollection().insertData(jsondata)

    def lastData(self):
        return self.lastdata


class IncorrectSourceError(Exception):
    pass
