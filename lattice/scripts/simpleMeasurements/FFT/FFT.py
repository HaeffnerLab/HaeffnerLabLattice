import sys; 
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\PulseSequences')
import labrad
import numpy as np
from PulseSequences.TimeRes_FFT import TimeResolved

class measureFFT():
    def __init__(self, cxn, recordTime, average, freqSpan, freqOffset, savePlot = False):
        self.average = average
        self.recordTime = recordTime
        self.defineServers(cxn)
        centerFreq = self.getCenterFreq()
        self.timeRes = float(self.pulser.get_timetag_resolution())
        self.freqs = self.computeFreqDomain(recordTime, freqSpan,  freqOffset, centerFreq)
        self.programPulseSequence(recordTime)
        self.savePlot = savePlot
    
    def getCenterFreq(self):
        rffreq = float(self.trap_drive.frequency())*1e6 #in Hz
        return rffreq
    
    def computeFreqDomain(self, recordTime, freqSpan, freqOffset, centerFreq):
        freqRes = 1.0 / recordTime
        minFreq = centerFreq + freqOffset - freqSpan / 2.0
        maxFreq = centerFreq + freqOffset + freqSpan / 2.0
        freqs = np.arange(minFreq, maxFreq, freqRes)
        return freqs

    def defineServers(self, cxn):
        self.trap_drive = cxn.trap_drive
        self.dv = cxn.data_vault
        self.pulser = cxn.pulser
    
    def programPulseSequence(self, recordTime):
        params = {
                  'recordTime': recordTime
                  }
        seq = TimeResolved(self.pulser)
        self.pulser.new_sequence()
        seq.setVariables(**params)
        seq.defineSequence()
        self.pulser.program_sequence()
    
    def getTotalPower(self):
        '''computers the total power in the spectrum of the given frequenceis'''
        pwr = self.getPowerSpectrum()
        totalPower = np.sum(pwr)  
        print 'Total Power {}'.format(totalPower)
        return totalPower
    
    def getPeakArea(self, ptsAround):
        '''Finds the maximum of the power spectrum, computers the area of the peak using ptsAround, then subtracts the background'''
        pwr = self.getPowerSpectrum()
        maxindex = pwr.argmax()
        if (maxindex - ptsAround < 0) or (maxindex + 3) > pwr.size:
            raise Exception("FFT Peak found too close to boundary")
        peakArea = np.sum(pwr[maxindex - ptsAround: maxindex + ptsAround + 1])
        background = (np.sum(pwr) - peakArea) / (pwr.size - 2 * ptsAround + 1) #average height of a point outside the peak
        peakArea = peakArea - background * (2 * ptsAround + 1) #background subtraction
        print 'Peak Area {}'.format(peakArea)
        return peakArea
        
    def getPowerSpectrum(self):
        pwr = np.zeros_like(self.freqs)
        for i in range(self.average):
            print 'iteration {0} out of {1}'.format(i+1, self.average)
            self.pulser.reset_timetags()
            self.pulser.start_single()
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
            timetags = self.pulser.get_timetags().asarray
            print 'photons counted', timetags.size
            pwr += self.getFFTpwr(timetags)
        pwr = pwr / float(self.average)
        if self.savePlot: self.saveData(pwr)
        return pwr
        
    def saveData(self, pwr):
        self.dv.cd(['','QuickMeasurements','FFT'],True)
        name = self.dv.new('FFT',[('Freq', 'Hz')], [('Power','Arb','Arb')] )
        data = np.array(np.vstack((self.freqs,pwr)).transpose(), dtype = 'float')
        self.dv.add_parameter('plotLive',True)
        self.dv.add(data)
        print 'Saved {}'.format(name)
       
    def getFFTpwr(self, timetags):
        '''uses the timetags to compute the fft power at freqs
        normalization such that the total power across all frequency is 1'''
        mat = np.exp(-1.j*2.0*np.pi*np.outer(self.freqs, timetags))
        fft = mat.sum(axis=1)
        pwr = np.abs(fft)**2.0 
        if timetags.size > 0:
            #normalizes such that total of the complete power spectrum is 1:
            #timetags.size is the initial area of the signal while N is the length of the array, see Parseval's theorem
            N = self.recordTime / self.timeRes
            pwr = pwr / (N * timetags.size) 
        else:
             pwr = np.zeros_like(self.freqs)
        del(mat,fft)
        return pwr

if  __name__ == '__main__':
    cxn = labrad.connect()
    recordTime = 0.5 #seconds
    average = 4
    freqSpan = 300.0 #Hz 
    freqOffset = -310.0 #Hz, the offset between the counter clock and the rf synthesizer clock
    fft = measureFFT(cxn, recordTime, average, freqSpan, freqOffset, savePlot = True)
    totalPower = fft.getTotalPower()
    #peakArea = fft.getPeakArea(ptsAround = 3)