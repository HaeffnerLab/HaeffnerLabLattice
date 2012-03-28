import sys; 
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\PulseSequences')
import labrad
import numpy as np
import time
from scriptLibrary import dvParameters 
from PulseSequences.TimeRes_FFT import TimeResolved

centerFreq = 14799400#14998866#15.00*10**6
ptsAround = 4
recordTime = 1 #seconds
iterations = 50
average = 2
#program pulse sequence for triggering time resolved

params = {
              'recordTime': 1.0#100*1e-3,
          }

#connect and define servers we'll be using
cxn = labrad.connect()
cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
dv = cxn.data_vault
pulser = cxn.pulser
timeResolution = 10e-9 # not used
freqRes = 1.0 / recordTime

# program pulser
seq = TimeResolved(pulser)
pulser.new_sequence()
seq.setVariables(**params)
seq.defineSequence()
pulser.program_sequence()

freqs = centerFreq + np.arange(-ptsAround,ptsAround + 1) * freqRes

def getFFTpwr(timetags):
    mat = np.exp(-1.j*2.0*np.pi*np.outer(freqs, timetags))
    fft = mat.sum(axis=1)
    pwr = np.abs(fft)**2.0
    pwr = pwr / timetags.size
    del(mat,fft)
    return pwr

dv.cd(['','QuickMeasurements','FFTlive'],True)
dv.new('FFT',[('time', 'arb')], [('Power','Arb','Arb')] )
for i in range(iterations):
    pwr = np.zeros_like(freqs)
    for j in range(average):
        pulser.reset_timetags()
        pulser.start_single()
        pulser.wait_sequence_done()
        pulser.stop_sequence()
        timetags = pulser.get_timetags().asarray
        print 'timetag size', timetags.size
        pwr += getFFTpwr(timetags)
    pwr = pwr.sum() #find the total power across the frequencies 
    dv.add([i,pwr])
print 'DONE'


