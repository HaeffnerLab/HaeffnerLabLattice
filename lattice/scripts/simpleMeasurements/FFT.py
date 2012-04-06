import sys; 
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\PulseSequences')
import labrad
import numpy as np
from PulseSequences.TimeRes_FFT import TimeResolved

recordTime = 0.5 #seconds
average = 4
freqSpan = 300.0 #Hz 
freqOffset = -310.0 #Hz, the offset between the counter clock and the rf synthesizer clock

#program pulse sequence for triggering time resolved
params = {
              'recordTime': recordTime
          }

#connect and define servers we'll be using
cxn = labrad.connect()
cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
dv = cxn.data_vault
rf = cxn.lattice_pc_hp_server
pulser = cxn.pulser
freqRes = 1.0 / recordTime
rffreq = float(rf.getfreq())*1e6 #in Hz
minFreq = rffreq + freqOffset - freqSpan/2.0
maxFreq = rffreq + freqOffset + freqSpan/2.0
# program pulser
seq = TimeResolved(pulser)
pulser.new_sequence()
seq.setVariables(**params)
seq.defineSequence()
pulser.program_sequence()
timeRes = float(pulser.get_timetag_resolution())
freqs = np.arange(minFreq,maxFreq,freqRes)

def getFFTpwr(timetags):
    '''uses the timetags to compute the fft power at freq
    normalization such that the total power across all frequency is 1'''
    mat = np.exp(-1.j*2.0*np.pi*np.outer(freqs, timetags))
    fft = mat.sum(axis=1)
    pwr = np.abs(fft)**2.0 
    if timetags.size > 0:
        #normalizes such that total of the complete power spectrum is 1:
        #timetags.size is the initial area of the signal while N is the length of the array, see Parseval's theorem
        N = recordTime / timeRes
        pwr = pwr / (N * timetags.size) 
    else:
        pwr = np.zeros_like(freqs)
    del(mat,fft)
    return pwr

pwr = np.zeros_like(freqs)
for i in range(average):
    print 'iteration {0} out of {1}'.format(i+1, average)
    pulser.reset_timetags()
    pulser.start_single()
    pulser.wait_sequence_done()
    pulser.stop_sequence()
    timetags = pulser.get_timetags().asarray
    print 'photons counted', timetags.size
    pwr += getFFTpwr(timetags) / (timetags.size / recordTime) #normalize to fluorescence rate
totalPower = np.sum(pwr)  
totalPower = totalPower / float(average) #normalizing to the number of averaging iterations
totalPower = totalPower*1e9 #to make numbers bigger, the size is arbitrary anyway
#saving to DV
dv.cd(['','QuickMeasurements','FFT'],True)
name = dv.new('FFT',[('Freq', 'Hz')], [('Power','Arb','Arb')] )
data = np.array(np.vstack((freqs,pwr)).transpose(), dtype = 'float')
dv.add_parameter('plotLive',True)
dv.add(data)
print 'Saved {}'.format(name)
print 'Total Power {}'.format(totalPower)
print 'DONE'