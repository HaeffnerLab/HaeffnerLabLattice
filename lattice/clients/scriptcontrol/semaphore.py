from labrad.server import LabradServer, setting
import time
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread

class Semaphore(LabradServer):
    """Houses the Blocking Function"""
    name = "Semaphore"
    
    onStatusChange = Signal(111111, 'signal: status parameter change', 's')
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
        self.paramDict['Global'] = {}
        for experiment in experiments:
            self.paramDict[experiment] = {}
            self.paramDict[experiment]['Block'] = False
            self.paramDict[experiment]['Status'] = 'Stopped'
            self.paramDict[experiment]['Continue'] = True # If set to False, then the script should know to clean itself up.
    
    #####
    
    
    # SET INITIAL VALUES HERE!!! Labrad registry?
    
    
    ####
    
    def _setGlobalParameters(self, parameters, values):
        for parameter, value in parameters, values:
            self.paramDict['Global'][parameter] = value

    def _getGlobalParameters(self, parameters):
        values = []
        for parameter in parameters:
            values.append(self.paramDict['Global'][parameter])
        return values

    def _setExperimentParameters(self, experiment, parameters, values):
        for parameter, value in parameters, values:
            self.paramDict[experiment][parameter] = value

    def _getExperimentParameters(self, experiment, parameters):
        values = []
        for parameter in parameters:
            values.append(self.paramDict[experiment][parameter])
        return values        
    
    @inlineCallbacks            
    def _blockExperiment(self, experiment):
        self.paramDict[experiment]['Status'] = 'Paused'
        self.onStatusChange(experiment, self.listeners)
        while(1):
            yield deferToThread(time.sleep, .5)
            if (self.paramDict[experiment]['Block'] == False):
                if (self.paramDict[experiment]['Continue'] == True):
                    self.paramDict[experiment]['Status'] = 'Running'
                else:
                    self.paramDict[experiment]['Status'] = 'Stopped'
            self.onStatusChange(experiment, self.listeners)
            returnValue(self.paramDict[experiment]['Continue'])                                        

    @setting(0, "Initialize Experiments", experiments = '*s', returns = '')
    def initializeExperiments(self, c, experiments):
        """Reserve Parameter Space For Each Experiment"""
        self._initializeExperiments(experiments)
        self._getRegistryValues(experiments)

    @setting(1, "Set Global Parameters", parameters = '*s', values = '*v', returns = '')
    def setGlobalParameters(self, c, parameters, values):
        """Set Global Parameters"""
        self._setGlobalParameters(parameters)

    @setting(2, "Set Experiment Parameters", experiment = 's', parameters = '*s', values = '*v', returns = '')
    def setExperimentParameters(self, c, experiment, parameters, values):
        """Set Experiment Parameters"""
        self._setExperimentParameters(experiment, parameters, values)

    @setting(3, "Get Global Parameters", parameters = '*s', returns = '*v')
    def getGlobalParameters(self, c, parameters):
        """Get Global Parameter Values"""
        values = self._getGlobalParameters(parameters)
        return values

    @setting(4, "Get Experiment Parameters", experiment = 's', parameters = '*s', returns = '*v')
    def getExperimentParameters(self, c, experiment, parameters):
        """Get Experiment Parameter Values"""
        values = self._getExperimentParameters(experiment, parameters)
        return values
 
    @setting(10, "Block Experiment", experiment = 's', returns="b")
    def blockExperiment(self, c, experiment):
        """Update and get the number."""
        result = self._blockExperiment()
        return result
    




if __name__ == "__main__":
    from labrad import util
    util.runServer(Semaphore())