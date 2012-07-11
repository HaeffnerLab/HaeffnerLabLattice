import sys; 
sys.path.append('/home/lattice/LabRAD/lattice/scripts')
import labrad
import numpy as np
from PulseSequences.TimeResolvedRecord import TimeResolved
from processFFT import processFFT

class measureFFT():
    ''' Scripts for performing FFT measurements '''
    def __init__(self, cxn, recordTime, average, freqSpan, freqOffset, savePlot = False):
        self.processor = processFFT()
        self.average = average
        self.recordTime = recordTime
        self.defineServers(cxn)
        centerFreq = self.getCenterFreq()
        self.timeRes = float(self.pulser.get_timetag_resolution())
        self.freqs = self.processor.computeFreqDomain(recordTime, freqSpan,  freqOffset, centerFreq)
        self.programPulseSequence(recordTime)
        self.savePlot = savePlot
    
    def getCenterFreq(self):
        rffreq = float(self.trap_drive.frequency())*10.0**6 #in Hz
        return rffreq

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
        '''computers the total power in the spectrum of the given frequencies'''
        spectrum = self.getPowerSpectrum()
        totalPower = self.processor.totalPower(spectrum)
        print 'Total Power {}'.format(totalPower)
        return totalPower
    
    def getPeakArea(self, ptsAround):
        '''Finds the maximum of the power spectrum, computers the area of the peak using ptsAround, then subtracts the background'''
        spectrum = self.getPowerSpectrum()
        peakArea = self.processor.peakArea(spectrum, ptsAround)
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
            pwr += self.processor.getPowerSpectrum(self.freqs, timetags, self.recordTime, self.timeRes)
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

if  __name__ == '__main__':
    cxn = labrad.connect()
    recordTime = 0.5 #seconds
    average = 4
    freqSpan = 300.0 #Hz 
    freqOffset = -310.0 #Hz, the offset between the counter clock and the rf synthesizer clock
    fft = measureFFT(cxn, recordTime, average, freqSpan, freqOffset, savePlot = True)
    #totalPower = fft.getTotalPower()
    peakArea = fft.getPeakArea(ptsAround = 3)