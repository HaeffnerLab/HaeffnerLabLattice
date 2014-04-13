import numpy as np

class processFFT():
    '''Mathematical operations useful for FFT processing. These are independent from LabRAD communication.'''
        
    def computeFreqDomain(self, recordTime, freqSpan, freqOffset, centerFreq):
        '''computers the domain of frequencies for the given recording time, and the frequency range'''
        freqRes = 1.0 / recordTime
        minFreq = centerFreq + freqOffset - freqSpan / 2.0
        maxFreq = centerFreq + freqOffset + freqSpan / 2.0
        freqs = np.arange(minFreq, maxFreq, freqRes)
        return freqs

    def totalPower(self, spectrum):
        '''computers the total power in the spectrum'''
        totalPower = np.sum(spectrum)  
        return totalPower
    
    def peakArea(self, spectrum, ptsAround):
        '''Finds the maximum of the power spectrum, computers the area of the peak using ptsAround, and subtracts the background'''
        maxindex = spectrum.argmax()
        if (maxindex - ptsAround < 0) or (maxindex + 3) > spectrum.size:
            raise Exception("FFT Peak found too close to boundary")
        peakArea = np.sum(spectrum[maxindex - ptsAround: maxindex + ptsAround + 1])
        background = (np.sum(spectrum) - peakArea) / (spectrum.size - (2 * ptsAround + 1)) #average height of a point outside the peak
        peakArea = peakArea - background * (2 * ptsAround + 1) #background subtraction
        return peakArea
    
    def getPowerSpectrum(self, freqs, timetags, recordTime, timeResolution):
        '''uses the timetags to compute the fft power at freqs
        normalization such that the total power across all frequency is 1'''
        mat = np.exp(-1.j*2.0*np.pi*np.outer(freqs, timetags))
        fft = mat.sum(axis=1)
        pwr = np.abs(fft)**2.0 
        if timetags.size > 0:
            #normalizes such that total of the complete power spectrum is 1:
            #timetags.size is the initial area of the signal while N is the length of the array, see Parseval's theorem
            N = recordTime / timeResolution
            pwr = pwr / (N * timetags.size) 
        else:
             pwr = np.zeros_like(freqs)
        del(mat,fft)
        return pwr