from dataProcess import dataProcess
import numpy as np

import matplotlib
matplotlib.use('qt4agg')
from matplotlib import pyplot

class timeResolvedFFT(dataProcess):
    """
    Performs FFT of time resolved data. Saves the result as a graph.
    @inputs: timelength is the timelength of the original trace where points are recorded with a certain resolution
    """
    name = 'timeResolvedFFT'
    inputsRequired = ['resolution','duration']
    inputsOptional = []
    
    def initialize(self):
        self.resolution = self.inputDict['resolution']
        self.duration = self.inputDict['duration']
        self.freqs = None
        self.ampl = None
        
    def processNewData(self, timetags):
        timetags=timetags.asarray
        totalCounts = timetags.size
        arrLength = int(self.duration / self.resolution)
        data = np.zeros(arrLength)
        inds = np.array(timetags / self.resolution, dtype = 'int')
        print inds
        data[inds] = 1
        print 'total counts:', totalCounts
        print timetags
        print self.resolution
        fft = np.fft.rfft(data)
        freqs = np.fft.fftfreq(arrLength, d = float(self.resolution))
        self.freqs = np.abs(freqs[0:(arrLength/2) + 1])
        self.power = np.abs(fft)**2  / totalCounts
        print self.power.max()
        index = self.power.argmax()
        print 'index', index
        print 'freq',self.freqs[index]
        print 'mean', self.power.mean()
        del(fft)
        del(timetags)
    
    def getResult(self):
        self.plotResult()
        print 'in returning result'
#        self.result = np.hstack((self.freqs,self.power))
#        return self.result
        return 0

    def plotResult(self):
        print 'plotting'
        print self.freqs[1]
        print self.freqs.max()
        print self.freqs.size
        print self.power.size
        #pyplot.plot(self.freqs,self.power)# self.power)
        #pyplot.xlim([0,10000])
        #pyplot.xlim([14.9*10**6,15.1*10**6])
        #pyplot.xlim([14.99880*10**6,14.99894*10**6])
        #pyplot.ylim([0,600])
        pyplot.ylim([0,0.1])
        pyplot.savefig('liveFFT')
        pyplot.close()
        print 'done saving figure'