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
                                                           ('number_of_bins',50),
                                                           ('background_kc/sec',0)
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
        providedDict = {}
        [newargs,newvals] = zip(*newinputs)
        for defaultarg,defaultval in defaultinputs:
            if defaultarg in newargs:
                providedDict[defaultarg] = newvals[newargs.index(defaultarg)]
            else:
                providedDict[defaultarg] = defaultval
        func(newdata, **providedDict)
            
    def processTest(self, newdata, inputs):
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
            self.processTimeResolvedFFT(newdata)
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

    #@param bins: number of bins for the collected data
    #@param timestep: time resolution of the data
    #@param background: background counts in kc/sec 

    def heatingRateBinning(self, newdata, bins, timestep, background):
        if self.totalProcessedData is None: #first run, configuring output dimensions and setting up time axis
            firstPoint = newdata[0]
            timeresolved = np.array(firstPoint[1])
            b = bitarray.bitarray()
            decoded = base64.b64decode( timeresolved )
            b.fromstring( decoded )
            self.dataLength = len( b )
            self.totalProcessedData = np.zeros([bins,2])
            self.elemsperbin = self.dataLength / bins 
            bintime = timestep*self.elemsperbin
            self.totalProcessedData[:,0] = np.arange(bins)*bintime#setting up the time axis
            self.resultParams = [[('Time', 'sec')], [('Counts','arb','arb')]] #convert to KC/sec
            self.backgroundperbin = (background * 1000.) * bintime
            self.heatingRateBinning(newdata)
        else:
            for i in range( len( newdata ) ):
                timeresolved = np.array(newdata[i][1])
                decoded = base64.b64decode( timeresolved )
                b = bitarray.bitarray()
                b.fromstring( decoded )
                if len( b ) != self.dataLength: print 'WARNING Not All Data Same Length, Some Data Not Processed'
                else:
                    timeresolvedarr = np.array( b )
                    newbinned = np.sum(timeresolvedarr[0:self.elemsperbin* bins].reshape(bins,self.elemsperbin),1)
                    newbinned = newbinned - self.backgroundperbin #background subtraction
                    self.totalProcessedData[:,1]  = newbinned  + self.totalProcessedData[:,1]
                    self.newResultReady = True