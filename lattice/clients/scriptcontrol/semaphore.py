from labrad.server import LabradServer, setting, Signal
import time
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread

class Semaphore(LabradServer):
    """Houses the Blocking Function"""
    name = "Semaphore"
    
    onStatusChange = Signal(111111, 'signal: status parameter change', '(s,s)')
#    onParameterChange = Signal(222222, 'signal: parameter change', 's')
       
    def initServer(self):
        
        self.listeners = set()  
        self.paramDict = {}
    
    def initContext(self, c):
        """Initialize a new context object."""
        self.listeners.add(c.ID)
    
    def expireContext(self, c):
        self.listeners.remove(c.ID)   
    
    def _initializeExperiments(self, experiments):
        self.experiments = experiments
        self.paramDict['Global'] = {}
        for experiment in experiments:
            self.paramDict[experiment] = {}
            self.paramDict[experiment]['General'] = {}
            self.paramDict[experiment]['General']['Block'] = False
            self.paramDict[experiment]['General']['Status'] = 'Stopped'
            self.paramDict[experiment]['General']['Continue'] = True # If set to False, then the SCRIPT should know to clean itself up.
        self._getRegistryParameters(experiments)
    
    @inlineCallbacks
    def _getRegistryParameters(self, experiments):
        # global
        yield self.client.registry.cd(['','Servers', 'Semaphore', 'Global'], True)
        parameterList = yield self.client.registry.dir()
        parameters = parameterList[1]
        for parameter in parameters:
            value = yield self.client.registry.get(parameter)
            self.paramDict['Global'][parameter] = value
        # experiments
        for experiment in experiments:        
            yield self.client.registry.cd(['','Servers', 'Semaphore'])
            yield self.client.registry.cd(experiment)
            parameterList = yield self.client.registry.dir()
            parameters = parameterList[1]
            for parameter in parameters:
                value = yield self.client.registry.get(parameter)
                self.paramDict[experiment][parameter] = value
    
    def _setGlobalParameter(self, parameter, value):
        self.paramDict['Global'][parameter] = value

    def _getGlobalParameter(self, parameter):
        value = self.paramDict['Global'][parameter]
        return value

    def _setExperimentParameter(self, experiment, parameter, value):
        self.paramDict[experiment][parameter] = value

    def _getExperimentParameter(self, experiment, parameter):
        value = self.paramDict[experiment][parameter]
        return value
    
    def _getGlobalParameterNames(self):
        names = self.paramDict['Global'].keys()
        return names
    
    def _getExperimentParameterNames(self, experiment):
        names = self.paramDict[experiment].keys()
        names.remove('General')
        return names
    
    def _getGeneralExperimentParameter(self, experiment, parameter):
        value = self.paramDict[experiment]['General'][parameter]
        return value

    def _setGeneralExperimentParameter(self, experiment, parameter, value):
        self.paramDict[experiment]['General'][parameter] = value
        if (parameter == 'Status'):
            self.onStatusChange((experiment, self.paramDict[experiment]['General']['Status']), self.listeners)
    
    def _scriptRequestExperimentParameters(self, experiment):
        parameters = []
        for key, value in zip(self.paramDict[experiment].keys(), self.paramDict[experiment].values()):
            if (key == 'General'):
                pass
            else:
                parameters.append((key, value[2]))
        return parameters
    
    @inlineCallbacks
    def _saveParametersToRegistry(self):
        '''save the latest parameters into registry'''
        # global
        yield self.client.registry.cd(['','Servers', 'Semaphore', 'Global'], True)
        parameters = self.paramDict['Global'].keys()
        for parameter in parameters:
            yield self.client.registry.set(parameter, self.paramDict['Global'][parameter])
            
        # experiments
        for experiment in self.experiments:        
            yield self.client.registry.cd(['','Servers', 'Semaphore'])
            yield self.client.registry.cd(experiment)
            parameters = self.paramDict[experiment].keys()
            for parameter in parameters:
                if (parameter == 'General'):
                    pass
                else: 
                    yield self.client.registry.set(parameter, self.paramDict[experiment][parameter])
        returnValue(True)
    
    
    @inlineCallbacks            
    def _blockExperiment(self, experiment):
#        self.paramDict[experiment]['General']['Status'] = 'Paused'        
        while(1):
            yield deferToThread(time.sleep, .5)
            if (self.paramDict[experiment]['General']['Block'] == False):
                if (self.paramDict[experiment]['General']['Continue'] == True):
                    pass
#                    self.paramDict[experiment]['General']['Status'] = 'Running'
                else:
                    self.paramDict[experiment]['General']['Status'] = 'Stopped'
                returnValue(self.paramDict[experiment]['General']['Continue'])

    @setting(0, "Initialize Experiments", experiments = '*s', returns = '')
    def initializeExperiments(self, c, experiments):
        """Reserve Parameter Space For Each Experiment"""
        self._initializeExperiments(experiments)

    @setting(1, "Set Global Parameter", parameter = 's', value = '*v', returns = '')
    def setGlobalParameter(self, c, parameter, value):
        """Set Global Parameter"""
        self._setGlobalParameter(parameter, value)

    @setting(2, "Set Experiment Parameter", experiment = 's', parameter = 's', value = '*v', returns = '')
    def setExperimentParameter(self, c, experiment, parameter, value):
        """Set Experiment Parameter"""
        self._setExperimentParameter(experiment, parameter, value)

    @setting(3, "Get Global Parameter", parameter = 's', returns = '*v')
    def getGlobalParameter(self, c, parameter):
        """Get Global Parameter Value"""
        value = self._getGlobalParameter(parameter)
        return value

    @setting(4, "Get Experiment Parameter", experiment = 's', parameter = 's', returns = '*v')
    def getExperimentParameter(self, c, experiment, parameter):
        """Get Experiment Parameter Value"""
        value = self._getExperimentParameter(experiment, parameter)
        return value

    @setting(5, "Get Global Parameter Names", returns = '*s')
    def getGlobalParameterNames(self, c):
        """Get Global Parameter Names"""
        parameterNames = self._getGlobalParameterNames()
        return parameterNames
    
    @setting(6, "Get Experiment Parameter Names", experiment = 's', returns = '*s')
    def getExperimentParameterNames(self, c, experiment):
        """Get Experiment Parameter Names"""
        parameterNames = self._getExperimentParameterNames(experiment)
        return parameterNames
    
    @setting(7, "Save Parameters To Registry", returns = 'b')
    def saveParametersToRegistry(self, c):
        """Get Experiment Parameter Names"""
        success = yield self._saveParametersToRegistry()
        returnValue(success)
        
    @setting(8, "Get General Experiment Parameter", experiment = 's', parameter = 's', returns = '?')
    def getGeneralExperimentParameter(self, c, experiment, parameter):
        value = self._getGeneralExperimentParameter(experiment, parameter)
        return value

    @setting(9, "Set General Experiment Parameter", experiment = 's', parameter = 's', value = '?', returns = '')
    def setGeneralExperimentParameter(self, c, experiment, parameter, value):
        self._setGeneralExperimentParameter(experiment, parameter, value)
    
    @setting(10, "Script Request Experiment Parameters", experiment = 's', returns = '*(sv)')
    def scriptRequestExperimentParameters(self, c, experiment):
        parameters = self._scriptRequestExperimentParameters(experiment)
        return parameters
        
    @setting(11, "Block Experiment", experiment = 's', returns="b")
    def blockExperiment(self, c, experiment):
        """Update and get the number."""
        result = self._blockExperiment(experiment)
        return result
    
    
    @setting(12, "Save", returns="")
    def save(self, c):
        """Save"""
        self.stopServer()
        print 'It is now safe to turn off your computer.'
    
    
if __name__ == "__main__":
    from labrad import util
    util.runServer(Semaphore())