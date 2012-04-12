import sys; 
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\PulseSequences')
import labrad
import numpy as np
from PulseSequences.TimeRes_FFT import TimeResolved

if ___name___ == '___main___':
    recordTime = 0.5 #seconds
    average = 4
    freqSpan = 300.0 #Hz 
    freqOffset = -310.0 #Hz, the offset between the counter clock and the rf synthesizer clock
    

class measureFFT():
    def __init___(self, recordTime, average, freqSpan, freqOffset):
        self.recordTime = recordTime
        self.average = average
        self.freqs = self.computeFreqDomain()
        self.freqSpan = freqSpan
        self.freqOffset = freqOffset
        cxn = labrad.connect()
        cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
    
    def computeFreqDomain(self, recordTime, freqSpan, freqOffset):
        freqRes = 1.0 / recordTime
        rffreq = float(rf.getfreq())*1e6 #in Hz
        minFreq = rffreq + freqOffset - freqSpan / 2.0
        maxFreq = rffreq + freqOffset + freqSpan / 2.0
        freqs = np.arange(minFreq, maxFreq, freqRes)

    def defineServers(self):
        
        self.dv = cxn.data_vault
        self.rf = cxn.lattice_pc_hp_server
        self.pulser = cxn.pulser
    
    def oneMeasurement(self):
        self.pulser.reset_timetags()
        self.pulser.start_single()
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        timetags = self.pulser.get_timetags().asarray
        print 'photons counted', timetags.size
        pwr += self.getFFTpwr(timetags)  #normalize to fluorescence rate
        
    def getFFTpwr(self, timetags):
        '''uses the timetags to compute the fft power at freqs
        normalization such that the total power across all frequency is 1'''
        mat = np.exp(-1.j*2.0*np.pi*np.outer(self.freqs, timetags))
        fft = mat.sum(axis=1)
        pwr = np.abs(fft)**2.0 
        if timetags.size > 0:
            #normalizes such that total of the complete power spectrum is 1:
            #timetags.size is the initial area of the signal while N is the length of the array, see Parseval's theorem
            N = recordTime / timeRes
            pwr = pwr / (N * timetags.size) 
        else:
             pwr = np.zeros_like(self.freqs)
        del(mat,fft)
        return pwr
        
    
    
#program pulse sequence for triggering time resolved
params = {
              'recordTime': recordTime
          }


# program pulser
seq = TimeResolved(pulser)
pulser.new_sequence()
seq.setVariables(**params)
seq.defineSequence()
pulser.program_sequence()
timeRes = float(pulser.get_timetag_resolution())




pwr = np.zeros_like(freqs)
for i in range(average):
    print 'iteration {0} out of {1}'.format(i+1, average)
    
#saving to DV
dv.cd(['','QuickMeasurements','FFT'],True)
name = dv.new('FFT',[('Freq', 'Hz')], [('Power','Arb','Arb')] )
data = np.array(np.vstack((freqs,pwr)).transpose(), dtype = 'float')
dv.add_parameter('plotLive',True)
dv.add(data)
totalPower = np.sum(pwr)  
totalPower = totalPower / float(average) #normalizing to the number of averaging iterations
print 'Saved {}'.format(name)
print 'Total Power {}'.format(totalPower)
print 'DONE'