'''
Created on Aug 11, 2011
@author: Michael Ramm
'''
from twisted.internet.defer import inlineCallbacks, returnValue#, , Deferred
from labrad.server import LabradServer, setting
#from labrad.errors import Error
#from twisted.internet.threads import deferToThread
#from twisted.internet import reactor
#import numpy as np
#from processingFunctions import processingFunctions
#from datetime import datetime

class automatorProcess():
    name  = None
    serversRequired = None
    serversOptional = None
    inputsRequired = None
    inputsOptional = None
    conflictingProccesses = None
    isRunning = None
    cxn = None
    
    def __init__(self, cxn, inputs):        
        self.cxn = cxn
        self.makeInputDict()
        self.setInputs(inputs)
        ####self.readyToExecute()
    
    @inlineCallbacks
    def readyToExecute(self):
        yield self.confirmServersUp()
        self.confirmHaveInputs()
        self.checkInputBounds()
    
    def checkInputBounds(self):
        pass
        
    def execute(self):
        pass
    
    def stop(self):
        pass
    
    def isRunning(self):
        return self.isRunning
    
    def confirmServersUp(self):
        for servername in self.serversRequired:
            if servername not in self.cxn.servers: raise("{} server not up".format(servername))
    
    def makeInputDict(self):
        self.inputDict = dict(self.inputsOptional)
        for req in self.inputsRequired:
            self.inputDict[req] = None
    
    def setInputs(self, newinputs):
        if newinputs is None: return
        newdict = dict(newinputs)
        for arg in self.inputDict.keys():
            if arg in newdict.keys(): inputDict[arg] = newdict[arg]
    
    def confirmHaveInputs(self):
        for req in self.inputsRequired:
            if self.inputDict[req] is None: raise("{} required input not set".format(req))

class processInfo():
    def __init__(self):
        self.processDict = {}
        self.running = []

    def addProcess(self, process):
        self.processDict[process.name] = process
    
    def getProcess(self, procName):
        return self.processDict[procName]
    
    def availableProcesses(self):
        return self.processDict.keys()
    
    def nonConflicting(self, procName):
        all = set(self.processDict.keys())
        conflicting = set(self.processDict[procName].conflictingProcesses)
        return all - conflicting
    
    def addRunningIstance(self, procName, instance):
        self.running.append( (procName,instance) )
    
    def getRunningInstance(self, procName):
        for name,instance in self.running:
            if name == procName: return instance
        return ''
    
    def removeRunningInstance(self, processNames,instance):
        for name,inst in self.running:
            if processName == name and inst == instance:
                self.running.remove((name,instss))

    def getRequiredInputs(self, procName):
        process = self.processDict[procName]
        return process.inputsRequired
    
    def getOptionalInputs(self, procName):
        process = self.processDict[procName]
        return process.inputsOptional
    
    def getRunningProcesses(self):
        running = set()
        for procName,instance in self.running:
            running.add(procName)
        return list(running)

class timeResolvedFullFFT(automatorProcess):
    """
    Performs and plots the FFT of Time Resolved Photons.
    """
    name = 'timeResolvedFullFFT'
    serversRequired = ['data_vault','timeresolvedfpga','pauls box']
    serversOptional = None
    conflictingProcesses = None
    inputsRequired = ['Measurement Time']
    inputsOptional = [
                      ('Data Vault Directory',"['','TimeResolvedCounts']"),
                      ('Iterations','1'),
                      ('runForever','False')
                      ]
    
    @inlineCallbacks
    def execute(self):
        print 'running'
        import time
        import numpy
        #import matplotlib
        #matplotlib.use('Qt4Agg')
        #from matplotlib import pyplot
        yield self.do()
    
    @inlineCallbacks    
    def do(self):
        print 'communicating'
        t = self.cxn.timeresolvedfpga
        yield t.set_time_length(0.010)
        yield t.perform_time_resolved_measurement()
        res = yield t.get_result_of_measurement()
        bytelength = res[0][0]
        timelength = res[0][1]
        arr = res[1].asarray
        positions = arr[0];
        elems = arr[1];

    #this process is much faster but equilvant to bitarray.fromstring(raw)
    #arr = numpy.array(b)

        result = numpy.zeros(( bytelength, 8), dtype = numpy.uint8)

        #goes from 255 to [1,1,1,1,1,1,1,1]
        def converter(x):
            str = bin(x)[2:].zfill(8)
            l = [int(s) for s in str]
            return l

        elems = map(converter , elems);
        result[positions] = elems
        result = result.flatten()
        fft = numpy.fft.rfft(result) #returns nice form, faster than fft for real inputs
        timestep = 5*10**-9 #nanoseconds, ADD this to server
        freqs = numpy.fft.fftfreq(result.size, d = timestep)
        freqs = numpy.abs(freqs[0:result.size/2 + 1])
        ampl = numpy.abs(fft)
        print 'done'
        #pyplot.plot(freqs, ampl)
        #pyplot.show()

#    @inlineCallbacks
#    def yieldsomething(self):
#        servers = yield self.cxn.manager.servers()
#        print servers
#        

class Automator( LabradServer ):
    """
    Server for performing routine tasks involving other servers. Servers as a central hub, controlling
    information flow among servers. 
    """
    name = 'Automator'
    def initServer(self):
        self.setupProcessInfo()  
    
    def setupProcessInfo(self):
        """
        Sets up the information about all available tasks
        """
        self.info = processInfo()
        self.info.addProcess(timeResolvedFullFFT)
        
    @setting(0, 'Get Available Processes', returns = '*s')
    def getAvailableProcesses(self, c):
        """
        Returns the list of names with processes available for running.
        """
        return self.info.availableProcesses()
    
    @setting(1, 'Get Inputs Required', processName = 's', returns = '*s')
    def getRequiredInputs(self, c, processName):
        """
        Returns the list of inputs for the given process.
        """
        if processName not in self.info.availableProcesses(): raise('Process Name Not Found')
        return self.info.getRequiredInputs(processName)
    
    
    @setting(2, 'Get Inputs Optional', processName = 's', returns = '*(ss)')
    def getOptionalInputs(self, c, processName):
        """
        Returns the list of optional inputs for the given process in the form (name, labrad dtype, default value)
        """
        if processName not in self.info.availableProcesses(): raise('Process Name Not Found')
        return self.info.getOptionalInputs(processName)
    
    @setting(3, 'Set Inputs', processName = 's',inputs = '*(sss)', returns = '')
    def setInputs(self, c, processName, inputs):
        """
        For the current context, sets the inputs for processName for future executations.
        """
        c['inputs'] = {processName : inputs }
        
    @setting(4, 'Get Running Processes', returns = '*s')
    def getRunningProcesses(self, c):
        """
        Returns processes that are currently executing
        """
        return self.info.getRunningProcesses()
        
    @setting(5, 'Start process execution', processName = 's', returns = '')
    def startProcessExecution(self, c, processName):
        """start
        Starts execution the specified process. Must run Set Inputs prior to execution to
        set any required inputs for the process.
        """
        process = self.info.getProcess(processName)
        if processName not in c['inputs'].keys():
            inputs = None
        else:
            inputs = c['inputs'][processName]
        cxn = self.client
        instance = process(cxn, inputs)
        yield instance.execute()
    
    @setting(6, 'Stop process execution', processName = 's')
    def stopProcess(self, c, processName):
        if processName not in self.info.getRunningProcesses(): raise('{} not currently running'.format(processName))
        instance = self.info.getRunningInstance(processName)
        instance.stop()
        self.info.removeRunningInstance(processName, instance)
    
    def initContext(self, c):
        c['inputs'] = {}
        
if __name__ == "__main__":
    from labrad import util
    util.runServer( Automator() )