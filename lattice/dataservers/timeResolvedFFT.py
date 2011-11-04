from dataProcess import dataProcess
import numpy as np

import matplotlib
matplotlib.use('qt4agg')
from matplotlib import pyplot

class timeResolvedFFT(dataProcess):
    """
    Performs FFT of time resolved data.
    @inputs: timelength is the timelength of the original trace where points are recorded with a certain resolution
    """
    name = 'timeResolvedFFT'
    inputsRequired = ['uncompressedArrByteLength','resolution']
    inputsOptional = [('bintime',100*10**-6)]
    
    def initialize(self):
        self.uncompressedLength16 = self.inputDict['uncompressedArrByteLength']
        self.resolution = self.inputDict['resolution']
        self.freqs = None
        self.ampl = None
        
    def processNewData(self, newdata):
        newdata = newdata.asarray
        nonZeroPositions = newdata[:,0]
        correspondingElements = newdata[:,1]
        #expanding compressed data to bit representation
        correspondingElements = map(self.converter , correspondingElements)
        self.uncompressedArr = np.zeros((self.uncompressedLength16, 16))
        self.uncompressedArr[nonZeroPositions] = correspondingElements
        self.uncompressedArr = self.uncompressedArr.flatten()
        totalCounts = np.sum(self.uncompressedArr)
        print totalCounts
        fft = np.fft.rfft(self.uncompressedArr) #returns nice form, faster than fft for real inputs
        print int(self.uncompressedLength16)
        freqs = np.fft.fftfreq(int(self.uncompressedLength16 * 16), d = float(self.resolution))
        self.freqs = np.abs(freqs[0:(self.uncompressedLength16 * 16 /2) + 1])
        self.ampl = np.abs(fft)
        self.power = np.vdot(fft,fft)
        del(fft)
    
    def getResult(self):
        pyplot.plot(self.freqs, self.power)
        #pyplot.xlim([14.5*10**6,15.5*10**6])
        pyplot.xlim([14.55*10**6,15.2*10**6])
        pyplot.ylim([0,1])
        print 'saving'
        pyplot.savefig('liveFFT')
        print 'done saving'
        pyplot.close()
        return 0
        self.result = np.hstack((self.freqs,self.ampl))

    @staticmethod
    #goes from 255 to [0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1]
    def converter(x):
        expr = bin(x)[2:].zfill(16)
        l = [int(s) for s in expr]
        return np.array(l)