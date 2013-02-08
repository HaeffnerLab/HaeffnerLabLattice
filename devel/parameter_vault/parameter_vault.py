"""
### BEGIN NODE INFO
[info]
name = Parameter Vault
version = 2.0
description = 
instancename = Parameter Vault

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue, Deferred

class ParameterVault(LabradServer):
    """
    Data Server for storing ongoing experimental parameters
    """
    name = "Parameter Vault"
    registryDirectory = ['','Servers', 'Parameter Vault']
    onParameterChange = Signal(612512, 'signal: parameter change', '(ss)')

    @inlineCallbacks
    def initServer(self):
        self.listeners = set()
        self.parameters = {}  
        yield self.load_parameters()
    
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
    def load_parameters(self):
        #recursively add all parameters to the dictionary
        yield self._addParametersInDirectory(self.registryDirectory, [])
        print self.parameters
    
    @inlineCallbacks
    def _addParametersInDirectory(self, topPath, subPath):
        yield self.client.registry.cd(topPath + subPath)
        directories,parameters = yield self.client.registry.dir()
        if subPath: #ignore parameters in the top level
            for parameter in parameters:
                value = yield self.client.registry.get(parameter)
                key = tuple(subPath + [parameter])
                self.parameters[key] = value
        for directory in directories:
            newpath = subPath + [directory]
            yield self._addParametersInDirectory(topPath, newpath)

    def _getParameterNames(self, path):
        names = []
        matching_keys = []
        for key in self.parameters.keys():
            if key[:len(path)] == path:
                matching_keys.append(key)
        if not len(matching_keys):
            raise Exception ("Wrong Directory or Empty Directory")
        else:
            for key in matching_keys:
                if len(key) == len(path) + 1: #exclude directories
                    names.append(key[-1])
        return names

    def _getDirectoryNames(self, path):
        names = set()
        matching_keys = []
        for key in self.parameters.keys():
            if key[:len(path)] == path:
                matching_keys.append(key)
        if not len(matching_keys):
            raise Exception ("Wrong Directory or Empty Directory")
        else:
            for key in matching_keys:
                if len(key) > len(path) + 1: #exclude parameters
                    names.add(key[len(path)])
        return list(names)
   
    @inlineCallbacks
    def save_parameters(self):
        '''save the latest parameters into registry'''
        regDir = self.registryDirectory
        for key, value in self.parameters.iteritems():
            key = list(key)
            parameter_name = key.pop()
            fullDir = regDir + key
            yield self.client.registry.cd(fullDir)
            yield self.client.registry.set(parameter_name, value)
    
    def check_parameter(self, name, value):
        t,item = value
        if t == 'parameter':
            assert item[0] <= item[2] <= item[1], "Parameter {} Out of Bound".format(name)
            return item[2]
        else:
            #paraeter not one of known values
            return value

    @setting(0, "Set Parameter", path = '*s', value = ['*v', 'v', 'b', 's', '*(sv)', '*s', '?'], returns = '')
    def setParameter(self, c, path, value):
        """Set Parameter"""
        key = path.astuple
        if key not in self.parameters.keys():
            raise Exception ("Parameter Not Found")
        self.parameters[key] = value
        notified = self.getOtherListeners(c)
        self.onParameterChange((list(path), value), notified)

    @setting(1, "Get Parameter", path = '*s', returns = ['*v', 'v', 'b', 's', '*(sv)', '*s', '?'])
    def getParameter(self, c, path):
        """Get Parameter Value"""
        key = path.astuple
        if key not in self.parameters.keys():
            raise Exception ("Parameter Not Found")
        value = self.parameters[key]
        result = self.check_parameter(key, value)
        return result

    @setting(2, "Get Parameter Names", path = '*s', returns = '*s')
    def getParameterNames(self, c, path):
        """Get Parameter Names"""
        path = path.astuple
        parameterNames = self._getParameterNames(path)
        return parameterNames
    
    @setting(3, "Save Parameters To Registry", returns = '')
    def saveParametersToRegistry(self, c):
        """Get Experiment Parameter Names"""
        yield self.save_parameters()
    
    @setting(4, "Get Directory Names", path = '*s', returns = '*s')
    def get_directory_names(self, c, path):
        """Get Directory Names, Use [] for top level directory"""
        path = path.astuple
        directoryNames = self._getDirectoryNames(path)
        return directoryNames    
        
    @setting(5, "Refresh Parameters", returns = '')
    def refresh_parameters(self, c):
        """Saves Parameters To Registry, then realods them"""
        yield self.save_parameters()
        yield self.load_parameters()
    
    @setting(6, "Reload Parameters", returns = '')
    def reload_parameters(self, c):
        """Discards current parameters and reloads them from registry"""
        yield self.load_parameters()
    
    @inlineCallbacks
    def stopServer(self):
        try:
            yield self.save_parameters()
        except AttributeError:
            #if values don't exist yet, i.e stopServer was called due to an Identification Rrror
            pass
      
if __name__ == "__main__":
    from labrad import util
    util.runServer(ParameterVault())