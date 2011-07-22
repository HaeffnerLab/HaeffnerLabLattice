'''
Created on Apr 27, 2011
@author: Michael Ramm, Christopher Reilly Haeffner Lab
'''
import numpy as np
import base64
import bitarray

class processingFunctions():
    def __init__(self):
        self.processMap = {
                           'test':{
                                   'function':self.processTest,
                                   'inputs':[]
                                   },
                           'TimeResolvedFFT':{
                                              'function':self.processTimeResolvedFFT,
                                              'inputs':[
                                                        ('timestep',10**-6)
                                                        ]
                                              },
                           'HeatingRateBinning':{
                                                 'function':self.heatingRateBinning,
                                                 'inputs':[
                                                           ('timestep',10**-6),
                                                           ('bin_duration',100*10**-6),
                                                           ]
                                                 }
                           }
        self.newResultReady = False
        self.totalRawData = None
        self.totalProcessedData = None
        self.resultParams = None
        
    def availableProcesses(self):
        return self.processMap.keys()
    
    def availableInputs(self, process):
        return self.processMap[process]['inputs']
    
    def getProcessFunc(self, process):
        return self.processMap[process]['function']
    
    def returnResult(self):
        self.newResultReady = False
        return self.totalProcessedData
    
    def getResultParams(self):
        return self.resultParams
    
    def process(self, processName, newdata, newinputs):
        func = self.processMap[processName]['function']
        defaultinputs = self.processMap[processName]['inputs']
        #replace the default values with provided ones
        providedDict = dict(defaultinputs)
        if newinputs is not None:
            newdict = dict(newinputs)
            for arg in providedDict.keys():
                if arg in newdict.keys(): providedDict[arg] = float(newdict[arg]) #float is necessary because otherwise newdict[agr] is Value(#, None)
        func(newdata, **providedDict)
            
    def processTest(self, newdata):
        print newdata
    
    def processTimeResolvedFFT(self, newdata, timestep):
        if self.totalProcessedData is None: #first run, configuring output dimensions and setting up frequency axis
            firstPoint = newdata[0]
            timeresolved = firstPoint[1]
            decoded = base64.b64decode( timeresolved )
            b = bitarray.bitarray()
            b.fromstring( decoded )
            dataLength = len(b)
            self.totalProcessedData = np.zeros([dataLength,2])
            freqs = np.fft.fftfreq(dataLength,d=timestep)
            self.totalProcessedData[:,0] = freqs
            self.resultParams = [[('Frequency', 'Hz')], [('Strength','arb','FFT')]]
            print self.resultParams[0]
            print self.resultParams[1]
            self.processTimeResolvedFFT(newdata, timestep)
        else:
            for i in range(len(newdata)) :
                timeresolved = newdata[i][1]
                decoded = base64.b64decode( timeresolved )
                b = bitarray.bitarray()
                b.fromstring( decoded )
                if len(b) == self.totalProcessedData.shape[0]:
                    nparr = np.array( b, dtype = int )
                    newProcessedData = np.abs(np.fft.fft(nparr))
                    self.totalProcessedData[:,1]  = newProcessedData  + self.totalProcessedData[:,1]
                    self.newResultReady = True
                else:
                    print 'WARNING Not All Data Same Length, Some Data Not Processed'


    def heatingRateBinning(self, newdata, bin_duration, timestep):
        """
        @param bin_duration: duration of each bin in seconds
        @param timestep: time resolution of the data in seconds
        """       
        def configureOutput(newdata, bin_duration, timestep):
            """
            Uses the first point to configure the output dimensions of the result
            """
            firstPoint = newdata[0]
            timeresolved = np.array(firstPoint[1])
            b = bitarray.bitarray()
            decoded = base64.b64decode( timeresolved )
            b.fromstring( decoded )
            self.dataLength = len( b )
            self.binNumber = np.floor(self.dataLength * timestep / bin_duration)
            self.totalProcessedData = np.zeros([self.binNumber,2])
            self.elemsperbin = np.floor(bin_duration / timestep)
            self.totalProcessedData[:,0] = np.arange(self.binNumber)*bin_duration#setting up the time axis
            self.resultParams = [[('Time', 'sec')], [('Counts','arb','arb')]] #convert to KC/sec
            
        def doProcess(newdata):
            for i in range( len( newdata ) ):
                timeresolved = np.array(newdata[i][1])
                decoded = base64.b64decode( timeresolved )
                b = bitarray.bitarray()
                b.fromstring( decoded )
                if len( b ) != self.dataLength: print 'WARNING Not All Data Same Length, Some Data Not Processed'
                else:
                    timeresolvedarr = np.array( b )
                    newbinned = np.sum(timeresolvedarr[0:self.elemsperbin* self.binNumber].reshape(self.binNumber,self.elemsperbin),1)
                    self.totalProcessedData[:,1]  = newbinned  + self.totalProcessedData[:,1]
        
        if self.totalProcessedData is None: #first run, configuring output dimensions and setting up time axis
            configureOutput(newdata, bin_duration, timestep)
        ####print self.totalProcessedData
        doProcess(newdata)
        ####print self.totalProcessedData
        self.newResultReady = True