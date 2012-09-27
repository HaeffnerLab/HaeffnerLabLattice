"""
### BEGIN NODE INFO
[info]
name = Semaphore
version = 1.0
description = 
instancename = Semaphore

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from labrad.server import LabradServer, setting, Signal
import time
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread

class Semaphore(LabradServer):
    """Houses the Blocking Function"""
    name = "Semaphore"
    registryDirectory = ['','Servers', 'Semaphore']
    onParameterChange = Signal(222222, 'signal: parameter change', ['(*s, *v)', '(*s, b)', '(*s, s)', '(*s, v)', '*s*(sv)', '(*s, *s)'])

    @inlineCallbacks
    def initServer(self):
        self.listeners = set()  
        self.parametersDict = {}
        yield self.loadDictionary()
    
    def initContext(self, c):
        """Initialize a new context object."""
        self.listeners.add(c.ID)
    
    def expireContext(self, c):
        self.listeners.remove(c.ID)   
        
    def getOtherListeners(self,c):
        notified = self.listeners.copy()
        notified.remove(c.ID)
        return notified
    
    @inlineCallbacks
    def loadDictionary(self):
        regDir = self.registryDirectory
        
        @inlineCallbacks
        def _addParametersInDirectory(topPath, subPath):
            yield self.client.registry.cd(topPath + subPath)
            directories,parameters = yield self.client.registry.dir()
            for parameter in parameters:
                value = yield self.client.registry.get(parameter)
                key = tuple(subPath + [parameter])
                self.parametersDict[key] = value
            for directory in directories:
                newpath = subPath + [directory]
                yield _addParametersInDirectory(topPath, newpath)
        #recursively add all parameters to the dictionary
        yield _addParametersInDirectory(regDir, []) 
    
    def _getParameterNames(self, path):
        names = []
        nest = self.parametersDict
        while True:
            try:
                key = path.pop(0)
            except IndexError:
                #reached the bottom directory
                for name,value in nest.iteritems():
                            if (type(value) != dict):
                                names.append(name)
                return names
            else:
                try:
                    nest = nest[key]
                except KeyError:
                    if key == '':
                        #edge case for top level directory
                        for name,value in nest.iteritems():
                            if (type(value) != dict):
                                names.append(name)
                        return names
                    else:
                        raise Exception ("Wrong Directory")
    
    def _getAllNames(self, path):
        nest = self.parametersDict
        try:
            for key in path[:-1]:
                nest = nest[key]
            names = nest[path[-1]].keys()
        # in the root directory
        except IndexError:
            names = nest.keys()
        return names    

    def _getDirectoryNames(self, path):
        allNames = self._getAllNames(path)
        parameterNames = self._getParameterNames(path)
        for parameterName in parameterNames:
            allNames.remove(parameterName)
        return allNames
#   
#    @inlineCallbacks
#    def _saveParametersToRegistry(self):
#        '''save the latest parameters into registry'''
#
#        topDir = ['','Servers', 'Semaphore']
#        while True:
#            for key self.parametersDict.keys():
#                
        
#        @inlineCallbacks
#        def saveParametersToRegistry(path, parametersDict):
#            #go to the right directory
#            if not len(path):
#                yield self.client.registry.cd(topDir, True)
#            else:
#                yield self.client.registry.cd(topDir + path, True)
#                
#            parameters = self._getParameterNames(path)
#            dirList = self._getAllNames(path)
#            for name in parameters:
#                dirList.remove(name)
#            #MR why do this can do _getDirectoryNames?
#            #set all parameters for the directory
#            for parameter in parameters:
#                yield self.client.registry.set(parameter, parametersDict[parameter])
#            #save parameters for every subdirectory
#            for directory in dirList:
#                if (directory != 'Semaphore'):
#                    #don't save Semaphore values to registry
#                    yield saveParametersToRegistry(path + [directory], parametersDict[directory])
#                    currentDir = yield self.client.registry.cd()
#                    if (currentDir != ['', 'Servers', 'Semaphore']): # first pass crappy solution i know        
#                        yield self.client.registry.cd(currentDir[0:-1])
#            
#        yield saveParametersToRegistry([], self.parametersDict)
   
    @inlineCallbacks            
    def _blockExperiment(self, path):
        blockPath = path + ['Semaphore', 'Block']
        continuePath = path + ['Semaphore', 'Continue'] 
        while(1):
            yield deferToThread(time.sleep, .5)
            if (self._getParameter(blockPath) == False):
                shouldContinue = self._getParameter(continuePath) 
                returnValue(shouldContinue)

    @setting(0, "Set Parameter", path = '*s', value = ['*v', 'v', 'b', 's', '*(sv)', '*s'], returns = '')
    def setParameter(self, c, path, value):
        """Set Parameter"""
        key = tuple(path)
        if key not in self.parametersDict.keys():
            raise Exception ("Parameter Not Found")
        self.parametersDict[key] = value
        notified = self.getOtherListeners(c)
        self.onParameterChange((path, value), notified)

    @setting(1, "Get Parameter", path = '*s', returns = ['*v', 'v', 'b', 's', '*(sv)', '*s'])
    def getParameter(self, c, path):
        """Get Parameter Value"""
        key = path.astuple
        if key not in self.parametersDict.keys():
            raise Exception ("Parameter Not Found")
        value = self.parametersDict[key]
        return value

    @setting(2, "Get Parameter Names", path = '*s', returns = '*s')
    def getParameterNames(self, c, path):
        """Get Parameter Names"""
        parameterNames = self._getParameterNames(path)
        return parameterNames
    
    @setting(7, "Save Parameters To Registry", returns = '')
    def saveParametersToRegistry(self, c):
        """Get Experiment Parameter Names"""
        self._saveParametersToRegistry()
        
    @setting(11, "Block Experiment", experiment = '*s', returns="b")
    def blockExperiment(self, c, experiment):
        """Can be called from the experiment to see whether it could be continued"""
        status = self._getParameter(experiment + ['Semaphore', 'Status'])
        if (status == 'Pausing'):
            self._setParameter(experiment + ['Semaphore', 'Block'], True)
            self._setParameter(experiment + ['Semaphore', 'Status'], 'Paused')
            self.onParameterChange((experiment + ['Semaphore', 'Status'], 'Paused'), self.listeners)
        result = yield self._blockExperiment(experiment)
        returnValue(result)
    
    @setting(12, "Refresh Semaphore", returns = '')
    def refreshSemaphore(self, c):
        """ Refreshes the Semaphore """
        yield self._saveParametersToRegistry()
        yield self._initializeExperiments()

    @setting(13, "Get Directory Names", path = '*s', returns = '*s')
    def getDirectoryNames(self, c, path):
        """Get Directory Names"""
        directoryNames = self._getDirectoryNames(path)
        return directoryNames    
    
    @setting(14, "Finish Experiment", path = '*s', returns = '')
    def finishExperiment(self, c, path, progress=None):
        if (progress == 100.0):
            self._setParameter(path + ['Semaphore', 'Status'], 'Finished')
            self.onParameterChange((path + ['Semaphore', 'Status'], 'Finished'), self.listeners)
            self.onParameterChange((path + ['Semaphore', 'Progress'], progress), self.listeners)
        else:
            self._setParameter(path + ['Semaphore', 'Status'], 'Stopped')
            self.onParameterChange((path + ['Semaphore', 'Status'], 'Stopped'), self.listeners)
    
    @setting(15, "Test Connection", returns = 's')
    def testConnection(self, c):
        return 'Connected!'
      
if __name__ == "__main__":
    from labrad import util
    util.runServer(Semaphore())