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
    
    onParameterChange = Signal(222222, 'signal: parameter change', ['(*s, *v)', '(*s, b)', '(*s, s)', '(*s, v)', '*s*(sv)', '(*s, *s)'])

    @inlineCallbacks
    def initServer(self):
        
        self.listeners = set()  
        self.parametersDict = {}
        yield self._initializeExperiments()
    
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
    def _initializeExperiments(self):
        topDir = ['','Servers', 'Semaphore']
        @inlineCallbacks
        def addParametersToDictionary(directory, parametersDict):
            yield self.client.registry.cd(directory)
            dirList = yield self.client.registry.dir()

            parameters = dirList[1]
            for parameter in parameters:
                value = yield self.client.registry.get(parameter)
                parametersDict[parameter] = value
            if ((len(dirList[0]) == 0) and (directory != 'Semaphore')):
                # Experiment!
                parametersDict['Semaphore'] = {}
                parametersDict['Semaphore']['Block'] = False
                parametersDict['Semaphore']['Status'] = 'Finished'
                parametersDict['Semaphore']['Continue'] = True # If set to False, then the SCRIPT should know to clean itself up.

            for directory in dirList[0]:
                parametersDict[directory] = {}
                yield addParametersToDictionary(directory, parametersDict[directory])
                currentDir = yield self.client.registry.cd()
                if (currentDir != ['', 'Servers', 'Semaphore']): # first pass crappy solution i know        
                    yield self.client.registry.cd(currentDir[0:-1])
        
        yield addParametersToDictionary(topDir, self.parametersDict)
        print 'Dictionary Initialized.'  
        
    def _setParameter(self, path, value):
        nest = self.parametersDict
        for key in path[:-1]:
            nest = nest[key]
        nest[path[-1]] = value

    def _getParameter(self, path):
        nest = self.parametersDict
        for key in path[:-1]:
            nest = nest[key]
        value = nest[path[-1]]
        if (type(value) == dict):
            raise Exception('Cannot return a directory.')
        return value
    
    def _getParameterNames(self, path):
        names = []
        nest = self.parametersDict
        try:
            for key in path[:-1]:
                nest = nest[key]
            for name in nest[path[-1]].keys():
                if (type(nest[path[-1]][name]) != dict):
                    names.append(name)
        # in the root directory
        except IndexError:
            for name in nest.keys():
                if (type(nest[name]) != dict):
                    names.append(name)
        return names
    
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
   
    @inlineCallbacks
    def _saveParametersToRegistry(self):
        '''save the latest parameters into registry'''

        topDir = ['','Servers', 'Semaphore']
        
        @inlineCallbacks
        def saveParametersToRegistry(path, parametersDict):
            if (len(path) == 0):
                yield self.client.registry.cd(topDir, True)
            else:
                yield self.client.registry.cd(topDir + path, True)
            parameters = self._getParameterNames(path)
            dirList = self._getAllNames(path)
            for name in parameters:
                dirList.remove(name)
            
            
            for parameter in parameters:
                yield self.client.registry.set(parameter, parametersDict[parameter])
            
            for directory in dirList:
                if (directory != 'Semaphore'):
                    #don't save Semaphore values to registry
                    yield saveParametersToRegistry(path + [directory], parametersDict[directory])
                    currentDir = yield self.client.registry.cd()
                    if (currentDir != ['', 'Servers', 'Semaphore']): # first pass crappy solution i know        
                        yield self.client.registry.cd(currentDir[0:-1])
            
        yield saveParametersToRegistry([], self.parametersDict)
   
    @inlineCallbacks            
    def _blockExperiment(self, path):
        blockPath = path + ['Semaphore', 'Block']
        continuePath = path + ['Semaphore', 'Continue'] 
        while(1):
            yield deferToThread(time.sleep, .5)
            if (self._getParameter(blockPath) == False):
                continueFactor = self._getParameter(continuePath) 
                returnValue(continueFactor)

    @setting(0, "Initialize Experiments", experiments = '*s', returns = '')
    def initializeExperiments(self, c, experiments):
        """Reserve Parameter Space For Each Experiment"""
        self._initializeExperiments(experiments)

    @setting(1, "Set Parameter", path = '*s', value = ['*v', 'v', 'b', 's', '*(sv)', '*s'], returns = '')
    def setParameter(self, c, path, value):
        """Set Parameter"""
        self._setParameter(path, value)
        notified = self.getOtherListeners(c)
        self.onParameterChange((path, value), notified)

    @setting(3, "Get Parameter", path = '*s', returns = ['*v', 'v', 'b', 's', '*(sv)', '*s'])
    def getParameter(self, c, path):
        """Get Parameter Value"""
        value = self._getParameter(path)
        return value

    @setting(5, "Get Parameter Names", path = '*s', returns = '*s')
    def getParameterNames(self, c, path):
        """Get Parameter Names"""
        parameterNames = self._getParameterNames(path)
        return parameterNames
    
    @setting(7, "Save Parameters To Registry", returns = '')
    def saveParametersToRegistry(self, c):
        """Get Experiment Parameter Names"""
        self._saveParametersToRegistry()
        
    @setting(11, "Block Experiment", experiment = '*s', returns="b")
    def blockExperiment(self, c, experiment, progress=None):
        """Update and get the number."""
        if (progress != None):
            self._setParameter(experiment + ['Semaphore', 'Progress'], progress)
            self.onParameterChange((experiment + ['Semaphore', 'Progress'], progress), self.listeners)
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