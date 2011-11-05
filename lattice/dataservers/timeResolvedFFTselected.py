from dataProcess import dataProcess
import numpy as np

class timeResolvedFFTselected(dataProcess):
    """
    Finds the fourier amplitudes at selected frequencies
    """
    name = 'timeResolvedFFTselected'
    inputsRequired = ['uncompressedArrByteLength','resolution','needFreqs']
    inputsOptional = []
    
    def initialize(self):
        self.uncompressedLength16 = self.inputDict['uncompressedArrByteLength']
        self.resolution = self.inputDict['resolution']
        self.freqs = self.inputDict['needFreqs']
        self.ampl = None
        
        
        
        self.timelength = self.inputDict['timelength']
        self.resolution = self.inputDict['resolution']
        
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
        self.power = fft * np.conjugate(fft) / totalCounts
        del(fft)
    
    def getResult(self):
        self.plotResult()
        print 'in returning result'
#        self.result = np.hstack((self.freqs,self.power))
#        return self.result
        return 0

    def plotResult(self):
        print 'saving'
        pyplot.plot(self.freqs, self.power)
        #pyplot.xlim([0,10000])
        pyplot.xlim([100000,400000])
#        pyplot.xlim([14.99880*10**6,14.99894*10**6])
        #pyplot.ylim([0,600])
        pyplot.ylim([0,100])
        pyplot.savefig('liveFFT')
        pyplot.close()
        print 'done saving figure'
        
    
    @staticmethod
    #goes from 255 to [0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1]
    def converter(x):
        expr = bin(x)[2:].zfill(16)
        l = [int(s) for s in expr]
        return np.array(l)