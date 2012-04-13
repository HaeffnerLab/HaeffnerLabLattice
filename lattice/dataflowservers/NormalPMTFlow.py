#Created on Aug 12, 2011
#@author: Michael Ramm

"""
### BEGIN NODE INFO
[info]
name = NormalPMTFlow
version = 1.2
description = 
instancename = NormalPMTFlow

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from labrad.server import LabradServer, setting, Signal
from twisted.internet.defer import Deferred, returnValue, inlineCallbacks
from twisted.internet.task import LoopingCall
import time

SIGNALID = 331483

class NormalPMTFlow( LabradServer):
    
    name = 'NormalPMTFlow'
    onNewCount = Signal(SIGNALID, 'signal: new count', 'v')
    
    @inlineCallbacks
    def initServer(self):
        #improve on this to start in arbitrary order
        self.dv = yield self.client.data_vault
        self.pulser = yield self.client.pulser
        self.collectTimeRange = yield self.pulser.get_collection_time()
        self.saveFolder = ['','PMT Counts']
        self.dataSetName = 'PMT Counts'
        self.dataSet = None
        self.collectTimes = {'Normal':0.100, 'Differential':0.100}
        self.lastDifferential = {'ON': 0, 'OFF': 0}
        self.currentMode = 'Normal'
        self.recording = LoopingCall(self._record)
        self.requestList = []
            
    @inlineCallbacks
    def makeNewDataSet(self):
        dir = self.saveFolder
        name = self.dataSetName
        yield self.dv.cd(dir, True)
        self.dataSet = yield self.dv.new(name, [('t', 'num')], [('KiloCounts/sec','866 ON','num'),('KiloCounts/sec','866 OFF','num'),('KiloCounts/sec','Differential Signal','num')])
        self.startTime = time.time()
        yield self.addParameters()
    
    @inlineCallbacks
    def addParameters(self):
        yield self.dv.add_parameter('plotLive',True)
        yield self.dv.add_parameter('startTime',self.startTime)
    
    @setting(0, 'Set Save Folder', folder = '*s', returns = '')
    def setSaveFolder(self,c , folder):
        yield self.dv.cd(folder, True)
        self.saveFolder = folder
    
    @setting(1, 'Start New Dataset', setName = 's', returns = '')
    def setNewDataSet(self, c, setName = None):
        """Starts new dataset, if name not provided, it will be the same"""
        if setName is not None: self.dataSetName = setName
        yield self.makeNewDataSet()
    
    @setting( 2, "Set Mode", mode = 's', returns = '' )
    def setMode(self,c, mode):
        """
        Start recording Time Resolved Counts into Data Vault
        """
        if mode not in self.collectTimes.keys(): raise('Incorrect Mode')
        if not self.recording.running:
            self.currentMode = mode
            yield self.pulser.set_mode(mode)
        else:
            yield self.dostopRecording()
            self.currentMode = mode
            yield self.pulser.set_mode(mode)
            yield self.dorecordData()

    @setting(3, 'getCurrentMode', returns = 's')
    def getCurrentMode(self, c):
        """
        Returns the currently running mode
        """
        return self.currentMode
    
    @setting(4, 'Record Data', returns = '')
    def recordData(self, c):
        """
        Starts recording data of the current PMT mode into datavault
        """
        yield self.dorecordData()
    
    @inlineCallbacks
    def dorecordData(self):
        self.keepRunning = True
        yield self.pulser.set_collection_time(self.collectTimes[self.currentMode], self.currentMode)
        yield self.pulser.set_mode(self.currentMode)
        if self.currentMode == 'Differential':
            yield self._programPulserDiff()
        if self.dataSet is None:
            yield self.makeNewDataSet()
        self.recording.start(self.collectTimes[self.currentMode]/2.0)
    
    @setting(5, returns = '')
    def stopRecording(self,c):
        """
        Stop recording counts into Data Vault
        """
        yield self.dostopRecording()
    
    @inlineCallbacks
    def dostopRecording(self):
        yield self.recording.stop()
        if self.currentMode == 'Differential':
            yield self._stopPulserDiff()
            
    @setting(6, returns = 'b')
    def isRunning(self,c):
        """
        Returns whether or not currently recording
        """
        return self.recording.running
        
    @setting(7, returns = 's')
    def currentDataSet(self,c):
        if self.dataSet is None: return ''
        name = self.dataSet[1]
        return name
    
    @setting(8, 'Set Time Length', timelength = 'v', mode = 's')
    def setTimeLength(self, c, timelength, mode = None):
        if mode is None: mode = self.currentMode
        if mode not in self.collectTimes.keys(): raise Exception('Incorrect Mode')
        if not self.collectTimeRange[0] <= timelength <= self.collectTimeRange[1]: raise Exception ('Incorrect Recording Time')
        self.collectTimes[mode] = timelength
        if mode == self.currentMode:
            yield self.recording.stop()
            yield self.pulser.set_collection_time(timelength, mode)
            if mode == 'Differential':
                yield self._stopPulserDiff()
                yield self._programPulserDiff()
            self.recording.start(timelength/2.0)
        else:
            yield self.pulser.set_collection_time(timelength, mode)
        
    @setting(9, 'Get Next Counts', type = 's', number = 'w', average = 'b', returns = ['*v', 'v'])
    def getNextCounts(self, c, type, number, average = False):
        """
        Acquires next number of counts, where type can be 'ON' or 'OFF' or 'DIFF'
        Average is optionally True if the counts should be averaged
        
        Note in differential mode, Diff counts get updates every time, but ON and OFF
        get updated every 2 times.
        """
        if type not in ['ON', 'OFF','DIFF']: raise('Incorrect type')
        if type in ['OFF','DIFF'] and self.currentMode == 'Normal':raise('in the wrong mode to process this request')
        if not 0 < number < 1000: raise('Incorrect Number')
        if not self.recording.running: raise('Not currently recording')
        d = Deferred()
        self.requestList.append(self.readingRequest(d, type, number))
        data = yield d
        if average:
            data = sum(data) / len(data)
        returnValue(data)
    
    @setting(10, 'Get Time Length', returns = 'v')
    def getMode(self, c):
        """
        Returns the current timelength of in the current mode
        """
        return self.collectTimes[self.currentMode]
    
    @setting(11, 'Get Time Length Range', returns = '(vv)')
    def get_time_length_range(self, c):
        return self.collectTimeRange
    
    @inlineCallbacks
    def _programPulserDiff(self):
        yield self.pulser.new_sequence()
        countRate = self.collectTimes['Differential']
        yield self.pulser.add_ttl_pulse('DiffCountTrigger', 0.0, 10.0e-6)
        yield self.pulser.add_ttl_pulse('DiffCountTrigger', countRate, 10.0e-6)
        yield self.pulser.add_ttl_pulse('866DP', 0.0, countRate)
        yield self.pulser.extend_sequence_length(2*countRate)
        yield self.pulser.program_sequence()
        yield self.pulser.start_infinite()
    
    
    @inlineCallbacks
    def _stopPulserDiff(self):
        yield self.pulser.complete_infinite_iteration()
        yield self.pulser.wait_sequence_done()
        yield self.pulser.stop_sequence()
        
    class readingRequest():
        def __init__(self, d, type, count):
            self.d = d
            self.count = count
            self.type = type
            self.data = []
        
        def is_fulfilled(self):
            return len(self.data) == self.count
    
    def processRequests(self, data):
        if not len(self.requestList): return
        for dataPoint in data:
            for item,req in enumerate(self.requestList):
                if dataPoint[1] != 0 and req.type == 'ON':
                    req.data.append(dataPoint[1])
                if dataPoint[2] != 0 and req.type == 'OFF':
                    req.data.append(dataPoint[1])
                if dataPoint[3] != 0 and req.type == 'DIFF':
                    req.data.append(dataPoint[1])
                if req.is_fulfilled():
                    req.d.callback(req.data)
                    del(self.requestList[item])
                    
    @inlineCallbacks
    def _record(self):
        rawdata = yield self.pulser.get_pmt_counts()
        if len(rawdata) != 0:
            if self.currentMode == 'Normal':
                toDataVault = [ [elem[2] - self.startTime, elem[0], 0, 0] for elem in rawdata] # converting to format [time, normal count, 0 , 0]
            elif self.currentMode =='Differential':
                toDataVault = self.convertDifferential(rawdata)
            self.processRequests(toDataVault) #if we have any requests, process them
            self.processSignals(toDataVault)
            yield self.dv.add(toDataVault)
    
    def processSignals(self, data):
        lastPt = data[-1]
        NormalCount = lastPt[1]
        self.onNewCount(NormalCount)
    
    def convertDifferential(self, rawdata):
        totalData = []
        for dataPoint in rawdata:
            t = str(dataPoint[1])
            self.lastDifferential[t] = float(dataPoint[0])
            diff = self.lastDifferential['ON'] - self.lastDifferential['OFF']
            totalData.append( [ dataPoint[2] - self.startTime, self.lastDifferential['ON'], self.lastDifferential['OFF'], diff ] )
        return totalData
            
if __name__ == "__main__":
    from labrad import util
    util.runServer( NormalPMTFlow() )