from dataProcess import dataProcess
import numpy as np
import math

class timeResolvedFFTselected(dataProcess):
    """
    Finds the fourier amplitudes at selected frequencies
    """
    name = 'timeResolvedFFTselected'
    inputsRequired = ['uncompressedArrByteLength','resolution','needFrequency','AvgPointSide']
    inputsOptional = []
    
    def initialize(self):
        self.uncompressedLength16 = self.inputDict['uncompressedArrByteLength']
        self.resolution = self.inputDict['resolution']
        self.centerFreq = self.inputDict['needFrequency']
        self.ptsAround = self.inputDict['AvgPointSide']
        
    def processNewData(self, newdata):
        newdata = newdata.asarray
        nonZeroPositions = newdata[:,0]
        correspondingElements = newdata[:,1]
        arrivalList = []
        #expanding compressed data to bit representation
        correspondingElements = map(self.converter , correspondingElements)
        #for every bit, calculate the time of photon arrival (in seconds)
        for byteNumber,bytePosition in enumerate(nonZeroPositions):
            byte = correspondingElements[byteNumber]
            for bitposition in byte.nonzero()[0]:
                arrivalTime = (bytePosition * 16 + bitposition)*self.resolution
                arrivalList.append(arrivalTime)
        arrivalList = np.array(arrivalList)
        totalCounts = len(arrivalList)
        #now that we know when photons arrived, calculate fourier components at the desired frequencies (in Hz)
        possibleFreqs = np.fft.fftfreq(int(self.uncompressedLength16 * 16), d = float(self.resolution))
        freqResolution = abs(possibleFreqs[1]-possibleFreqs[0])
        self.closestFreq = possibleFreqs[(np.abs(possibleFreqs- self.centerFreq)).argmin()]
        self.freqList = self.closestFreq * np.ones(2 * self.ptsAround + 1) + freqResolution * np.arange(-self.ptsAround,self.ptsAround+1)
        self.coeffMatrix = np.exp(-2 *math.pi * 1j *np.outer(arrivalList, self.freqList))
        self.coeffArr = np.sum(self.coeffMatrix, 0)
        self.powerArr = np.abs(self.coeffArr)**2 / totalCounts
        
#    def findTotalCounts(self,correspondingElements):
#        totalCount = 0
#        for element in correspondingElements:
#            expanded = self.converter(element)
#            totalCount += expanded.sum()
#        return totalCount
    
    def getResult(self):
        return np.vstack(np.array(self.freqList), np.array(self.powerArr))
#        return float(self.totalCount)
        
    
    @staticmethod
    #goes from 255 to [0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1]
    def converter(x):
        expr = bin(x)[2:].zfill(16)
        l = [int(s) for s in expr]
        return np.array(l)