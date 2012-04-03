import sys; 
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\PulseSequences')
import labrad
import numpy as np
from PulseSequences.TimeRes_FFT import TimeResolved

centerFreq = 14799400#14998866#15.00*10**6
ptsAround = 4
recordTime = 1.0 #seconds
iterations = 50
average = 5


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

freqs = centerFreq + np.arange(-ptsAround,ptsAround + 1) * freqRes

def getFFTpwr(timetags):
    mat = np.exp(-1.j*2.0*np.pi*np.outer(freqs, timetags))
    fft = mat.sum(axis=1)
    pwr = np.abs(fft)**2.0
    if timetags.size > 0:
        pwr = pwr / timetags.size
    else:
        pwr = np.zeros_like(freqs)
    del(mat,fft)
    return pwr

dv.cd(['','QuickMeasurements','FFTlive'],True)
dv.new('FFT',[('time', 'arb')], [('Power','Arb','Arb')] )
dv.add_parameter('plotLive',True)

for i in range(iterations):
    pwr = np.zeros_like(freqs)
    for j in range(average):
        pulser.reset_timetags()
        pulser.start_single()
        pulser.wait_sequence_done()
        pulser.stop_sequence()
        timetags = pulser.get_timetags().asarray
        print 'photons counted', timetags.size
        pwr += getFFTpwr(timetags)
    pwr = pwr / float(average) #normalize by averages
    totalPower = pwr.sum() #find the total power across the frequencies 
    dv.add([i,totalPower])
print 'DONE'
