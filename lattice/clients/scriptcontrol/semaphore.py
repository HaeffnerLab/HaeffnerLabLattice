from labrad.server import LabradServer, setting, Signal
import time
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread

class Semaphore(LabradServer):
    """Houses the Blocking Function"""
    name = "Semaphore"
    
#    onStatusChange = Signal(111111, 'signal: status parameter change', '(*s,s)')
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
#            print 'directory: ', directory
            yield self.client.registry.cd(directory)
            dirList = yield self.client.registry.dir()
#            print 'dirlist: ', dirList

            parameters = dirList[1]
            for parameter in parameters:
                value = yield self.client.registry.get(parameter)
                parametersDict[parameter] = value
            if ((len(dirList[0]) == 0) and (directory != 'Semaphore')):
                # Experiment!
                parametersDict['Semaphore'] = {}
                parametersDict['Semaphore']['Block'] = False
                parametersDict['Semaphore']['Status'] = 'Stopped'
                parametersDict['Semaphore']['Continue'] = True # If set to False, then the SCRIPT should know to clean itself up.
                
#            print 'global dict:, ', globalDict
#            print 'globalParametersDict: ',self.globalParametersDict
#            print 'experimentParametersDict', self.experimentParametersDict
            
#            dirs = dirList[0]
#            print 'dirs: ', dirs
            
#            for dir in dirs:
            for directory in dirList[0]:
#                print 'dir: ', dir
                parametersDict[directory] = {}
                yield addParametersToDictionary(directory, parametersDict[directory])
                currentDir = yield self.client.registry.cd()
                if (currentDir != ['', 'Servers', 'Semaphore']): # first pass crappy solution i know        
#                    print 'currentDir: ', currentDir
#                    print 'cd to one directory back'
#                    print currentDir[0:-1]
                    yield self.client.registry.cd(currentDir[0:-1])
        
        yield addParametersToDictionary(topDir, self.parametersDict)
        print 'Dictionary Initialized.'
#        self.globalParametersDict = topGlobalDict

        
        
#        for experiment in experiments:
#            self.paramDict[experiment] = {}
#            self.paramDict[experiment]['General'] = {}
#            self.paramDict[experiment]['General']['Block'] = False
#            self.paramDict[experiment]['General']['Status'] = 'Stopped'
#            self.paramDict[experiment]['General']['Continue'] = True # If set to False, then the SCRIPT should know to clean itself up.
#        self._getRegistryParameters(experiments)
#    
#        # global
#        yield self.client.registry.cd(['','Servers', 'Semaphore', 'Global'], True)
#        parameterList = yield self.client.registry.dir()
#        parameters = parameterList[1]
#        for parameter in parameters:
#            value = yield self.client.registry.get(parameter)
#            self.paramDict['Global'][parameter] = value
#        # experiments
#        for experiment in experiments:        
#            yield self.client.registry.cd(['','Servers', 'Semaphore'])
#            yield self.client.registry.cd(experiment)
#            parameterList = yield self.client.registry.dir()
#            parameters = parameterList[1]
#            for parameter in parameters:
#                value = yield self.client.registry.get(parameter)
#                self.paramDict[experiment][parameter] = value
    
        
    def _setParameter(self, path, value):
        nest = self.parametersDict
        for key in path[:-1]:
            nest = nest[key]
        nest[path[-1]] = value

    def _getParameter(self, path):
#        print self.parametersDict
#        value = reduce(dict.get, path, self.parametersDict)
        nest = self.parametersDict
        for key in path[:-1]:
            nest = nest[key]
        value = nest[path[-1]]
        if (type(value) == dict):
            raise Exception('Cannot return a directory.')
        return value
    
    
#    def _setGlobalParameter(self, parameter, value):
#        self.paramDict['Global'][parameter] = value
#        self.onGlobalParameterChange((parameter, value), self.listeners)
#
#    def _getGlobalParameter(self, parameter):
#        value = self.paramDict['Global'][parameter]
#        return value

#    def _setExperimentParameter(self, path, value):
#        self.paramDict[experiment][parameter] = value
#        self.onExperimentParameterChange((experiment, parameter, value), self.listeners)
#        print 'experiment signal'
#
#    def _getExperimentParameter(self, experiment, parameter):
#        value = self.paramDict[experiment][parameter]
#        return value
    
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
#        print 'in getallnames'
#        print 'getallnames path: ', path 
        try:
            for key in path[:-1]:
                nest = nest[key]
#                print 'getallnames nest: ', nest                
            names = nest[path[-1]].keys()
        # in the root directory
        except IndexError:
#            print 'in getallnames'
#            print 'getallnames path: ', path
#            print 'getallnames nest: ', nest 
            names = nest.keys()
        return names    

    def _getDirectoryNames(self, path):
        allNames = self._getAllNames(path)
        parameterNames = self._getParameterNames(path)
        for parameterName in parameterNames:
            allNames.remove(parameterName)
        return allNames

    
#    
#    def _getExperimentParameterNames(self, experiment):
#        names = self.paramDict[experiment].keys()
#        names.remove('General')
#        return names
    
#    def _getGeneralExperimentParameter(self, experiment, parameter):
#        value = self.paramDict[experiment]['General'][parameter]
#        return value
#
#    def _setGeneralExperimentParameter(self, experiment, parameter, value):
#        self.paramDict[experiment]['General'][parameter] = value
#        if (parameter == 'Status'):
#            self.onStatusChange((experiment, self.paramDict[experiment]['General']['Status']), self.listeners)
    
#    def _scriptRequestExperimentParameters(self, experiment):
#        parameters = []
#        for key, value in zip(self.paramDict[experiment].keys(), self.paramDict[experiment].values()):
#            if (key == 'General'):
#                pass
#            else:
#                parameters.append((key, value[2]))
#        return parameters
    
    @inlineCallbacks
    def _saveParametersToRegistry(self):
        '''save the latest parameters into registry'''

        topDir = ['','Servers', 'Semaphore']
        
        @inlineCallbacks
        def saveParametersToRegistry(path, parametersDict):
        # path = ['Test', 'Exp1']?, parametersDict is the dictionary representing the directory you're currently in.
            if (len(path) == 0):
#                print 'first time, ', path
                yield self.client.registry.cd(topDir, True)
            else:
#                print 'not first time: ', topDir + path
                yield self.client.registry.cd(topDir + path, True)
            parameters = self._getParameterNames(path)
#            print 'parameters: ', parameters
            dirList = self._getAllNames(path)
#            print 'dirlist first ', dirList
            for name in parameters:
                dirList.remove(name)
            
#            print 'dirList: ', dirList
            
            for parameter in parameters:
                yield self.client.registry.set(parameter, parametersDict[parameter])
#                print 'now me'
#                print parameter, parametersDict[parameter]
            
            for directory in dirList:
#                print 'dirList, from dirList for Loop: ', dirList
#                print 'directory, from dirList for Loop: ', directory
                if (directory != 'Semaphore'):
                    #don't save Semaphore values to registry
                    yield saveParametersToRegistry(path + [directory], parametersDict[directory])
                    currentDir = yield self.client.registry.cd()
    #                print 'current directory: ', directory
                    if (currentDir != ['', 'Servers', 'Semaphore']): # first pass crappy solution i know        
    #                    print 'currentDir: ', currentDir
    #                    print 'cd to one directory back'
    #                    print currentDir[0:-1]
    #                    print 'should switch to this directory: ', currentDir[0:-1]
                        yield self.client.registry.cd(currentDir[0:-1])
            
        yield saveParametersToRegistry([], self.parametersDict)

            
            ############################
#            
#
#
#            
#            yield self.client.registry.cd(directory)
#            dirList = yield self.client.registry.dir()
##            print 'dirlist: ', dirList
#
#            parameters = dirList[1]
##            print parameters
#            for parameter in parameters:
#                yield self.client.registry.set(parameter, parametersDict[parameter])
##            for dir in dirs:
#            for directory in dirList[0]:
##                print 'dir: ', directory
#                yield saveParametersToRegistry(directory, parametersDict[directory])
#                currentDir = yield self.client.registry.cd()
#                if (currentDir != ['', 'Servers', 'Semaphore']): # first pass crappy solution i know        
##                    print 'currentDir: ', currentDir
##                    print 'cd to one directory back'
##                    print currentDir[0:-1]
#                    yield self.client.registry.cd(currentDir[0:-1])
#        
#        saveParametersToRegistry(topDir, self.parametersDict)

#        
#        
#        
#        # global
#        yield self.client.registry.cd(['','Servers', 'Semaphore', 'Global'], True)
#        parameters = self.paramDict['Global'].keys()
#        for parameter in parameters:
#            yield self.client.registry.set(parameter, self.paramDict['Global'][parameter])
#            
#        # experiments
#        for experiment in self.experiments:        
#            yield self.client.registry.cd(['','Servers', 'Semaphore'])
#            yield self.client.registry.cd(experiment)
#            parameters = self.paramDict[experiment].keys()
#            for parameter in parameters:
#                if (parameter == 'General'):
#                    pass
#                else: 
#                    yield self.client.registry.set(parameter, self.paramDict[experiment][parameter])
#        returnValue(True)
#    
    
    @inlineCallbacks            
    def _blockExperiment(self, path):
#        self.paramDict[experiment]['General']['Status'] = 'Paused'
        blockPath = path + ['Semaphore', 'Block']
        continuePath = path + ['Semaphore', 'Continue'] 
#        statusPath = path + ['Semaphore', 'Status']       
        while(1):
            yield deferToThread(time.sleep, .5)
            if (self._getParameter(blockPath) == False):
                continueFactor = self._getParameter(continuePath) 
#                if (continueFactor == True):
#                    pass
##                    self.paramDict[experiment]['General']['Status'] = 'Running'
#                else:
#                    self._setParameter(statusPath, 'Stopped')
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
#        print (path, value)        

#    @setting(2, "Set Experiment Parameter", experiment = 's', parameter = 's', value = '*v', returns = '')
#    def setExperimentParameter(self, c, experiment, parameter, value):
#        """Set Experiment Parameter"""
#        self._setExperimentParameter(experiment, parameter, value)

    @setting(3, "Get Parameter", path = '*s', returns = ['*v', 'v', 'b', 's', '*(sv)', '*s'])
    def getParameter(self, c, path):
        """Get Parameter Value"""
        value = self._getParameter(path)
        return value

#    @setting(4, "Get Experiment Parameter", experiment = 's', parameter = 's', returns = '*v')
#    def getExperimentParameter(self, c, experiment, parameter):
#        """Get Experiment Parameter Value"""
#        value = self._getExperimentParameter(experiment, parameter)
#        return value

    @setting(5, "Get Parameter Names", path = '*s', returns = '*s')
    def getParameterNames(self, c, path):
        """Get Parameter Names"""
        parameterNames = self._getParameterNames(path)
        return parameterNames
    
#    @setting(6, "Get Experiment Parameter Names", experiment = 's', returns = '*s')
#    def getExperimentParameterNames(self, c, experiment):
#        """Get Experiment Parameter Names"""
#        parameterNames = self._getExperimentParameterNames(experiment)
#        return parameterNames
    
    @setting(7, "Save Parameters To Registry", returns = '')
    def saveParametersToRegistry(self, c):
        """Get Experiment Parameter Names"""
        self._saveParametersToRegistry()
        #returnValue(success)
        
#    @setting(8, "Get General Experiment Parameter", experiment = 's', parameter = 's', returns = '?')
#    def getGeneralExperimentParameter(self, c, experiment, parameter):
#        value = self._getGeneralExperimentParameter(experiment, parameter)
#        return value
#
#    @setting(9, "Set General Experiment Parameter", experiment = 's', parameter = 's', value = '?', returns = '')
#    def setGeneralExperimentParameter(self, c, experiment, parameter, value):
#        self._setGeneralExperimentParameter(experiment, parameter, value)
#    
#    @setting(10, "Script Request Experiment Parameters", experiment = 's', returns = '*(sv)')
#    def scriptRequestExperimentParameters(self, c, experiment):
#        parameters = self._scriptRequestExperimentParameters(experiment)
#        return parameters
        
    @setting(11, "Block Experiment", experiment = '*s', returns="b")
    def blockExperiment(self, c, experiment, progress=None):
        """Update and get the number."""
        if (progress != None):
            self._setParameter(experiment + ['Semaphore', 'Progress'], progress)
            self.onParameterChange((experiment + ['Semaphore', 'Progress'], progress), self.listeners)
        result = self._blockExperiment(experiment)
        return result
    
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
    def finishExperiment(self, c, path):
        self._setParameter(path + ['Semaphore', 'Status'], 'Stopped')
        self.onParameterChange((path + ['Semaphore', 'Status'], 'Stopped'), self.listeners)
        
#    @setting(12, "Save", returns="")
#    def save(self, c):
#        """Save"""
#        self.stopServer()
#        print 'It is now safe to turn off your computer.'
    
    
if __name__ == "__main__":
    from labrad import util
    util.runServer(Semaphore())