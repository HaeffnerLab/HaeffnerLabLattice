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
                           'test':self.processTest,
                           'TimeResolvedFFT':self.processTimeResolvedFFT,
                           'HeatingRateBinning':self.heatingRateBinning
                           }
        self.newResultReady = False
        self.totalRawData = None
        self.totalProcessedData = None
        self.resultParams = None
        
    def availableProcesses(self):
        return self.processMap.keys()
    
    def getProcessFunc(self, process):
        return self.processMap[process]
    
    def returnResult(self):
        self.newResultReady = False
        return self.totalProcessedData
    
    def getResultParams(self):
        return self.resultParams
    
    def process(self, processName, newdata):
        func = self.processMap[processName]
        func(newdata)
            
    def processTest(self, newdata):
        print newdata
    
    def processTimeResolvedFFT(self, newdata):
	timestep = 10**-6 #make this an arguement
        if self.totalProcessedData is None: #first run, configuring output dimensions and setting up frequency exis
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

    def heatingRateBinning(self, newdata):
	bins = 10 #make this an arguement
	timestep = 10**-6
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
		      self.totalProcessedData[:,1]  = newbinned  + self.totalProcessedData[:,1]
		      self.newResultReady = True