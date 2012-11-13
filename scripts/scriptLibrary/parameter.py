class Parameters():
    """Helper class for dealing with a list of parameters"""
    def __init__(self, parameterDict = None):
        if parameterDict is not None:
            self.dict = dict(parameterDict)
        else:
            self.dict = {}
    
    def addDict(self, newdict):
        for key in newdict.keys():
            self.dict[key] = newdict[key]
    
    def printDict(self):
        for key in self.dict.keys():
            print key , self.dict[key]