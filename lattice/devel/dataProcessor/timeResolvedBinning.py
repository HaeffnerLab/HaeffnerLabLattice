from dataProcess import dataProcess
import numpy as np

class timeResolvedBinning(dataProcess):
    """
    Bins the time resolved data
    @inputs: timelength is the timelength of the original trace where points are recorded with a certain resolution
    """
    name = 'timeResolvedBinning'
    inputsRequired = ['timelength','resolution']
    inputsOptional = [('bintime',100*10**-6)]
    
    def initialize(self):
        self.bintime = self.inputDict['bintime']
        self.timelength = self.inputDict['timelength']
        self.resolution = self.inputDict['resolution']
        self.binNumber = np.floor(self.timelength/self.bintime) #number of bins
        self.result = np.zeros([self.binNumber,2])
        self.result[:,0] = np.arange(self.binNumber) * self.bintime

    def processNewData(self, newdata):
        nonZeroPositions = newdata[0]
        correspondingElements = newdata[1]
        #expanding compressed data to bit representation
        elements = map(converter , elems)
        #for every bit, calculate the time of photon arrival and add to appropriate bin
        for byteNumber,bytePosition in enumerate(nonZeroPositions):
            byte = correspondingElements[byteNumber]
            for bitposition in byte.nonzeros()[0]:
                arrivalTime = (bytePosition * 8 + bitposition)*self.resolution
                
    def getResult(self):
        return self.result

  
    #goes from 255 to [1,1,1,1,1,1,1,1]
    def converter(x):
        st = bin(x)[2:].zfill(8)
        l = [int(s) for s in st]
        return l

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