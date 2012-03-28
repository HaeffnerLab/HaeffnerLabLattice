import sys; 
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\PulseSequences')
import labrad
import numpy as np
import time
from scriptLibrary import dvParameters 
from PulseSequences.TimeRes_FFT import TimeResolved

minFreq = 14.79938*10**6 #14.9985*10**6 #Hz  15.10935 @ 15.11///14.99938 14.9
maxFreq = 14.79943*10**6#14.9990*10**6  15.10940/// 14.99942
recordTime = 5.0 #seconds
average = 1
saveFFT = True
#program pulse sequence for triggering time resolved
params = {
              'recordTime': recordTime
          }

#connect and define servers we'll be using
cxn = labrad.connect()
cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
dv = cxn.data_vault
pulser = cxn.pulser
freqRes = 1.0 / recordTime

# program pulser
seq = TimeResolved(pulser)
pulser.new_sequence()
seq.setVariables(**params)
seq.defineSequence()
pulser.program_sequence()

freqs = np.arange(minFreq,maxFreq,freqRes)

def getFFTpwr(timetags):
    mat = np.exp(-1.j*2.0*np.pi*np.outer(freqs, timetags))
    fft = mat.sum(axis=1)
    pwr = np.abs(fft)**2.0
    pwr = pwr / timetags.size
    del(mat,fft)
    return pwr

pwr = np.zeros_like(freqs)
for i in range(average):
    print i
    pulser.reset_timetags()
    pulser.start_single()
    print 'triggered'
    pulser.wait_sequence_done()
    pulser.stop_sequence()
    timetags = pulser.get_timetags().asarray
    print 'got timetags'
    print 'timetag size', timetags.size
    pwr += getFFTpwr(timetags)
if saveFFT:
    dv.cd(['','QuickMeasurements','FFT'],True)
    dv.new('FFT',[('Freq', 'Hz')], [('Power','Arb','Arb')] )
    data = np.array(np.vstack((freqs,pwr)).transpose(), dtype = 'float')
    dv.add_parameter('plotLive',True)
    dv.add(data)
print 'DONE'