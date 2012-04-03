import sys; 
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\PulseSequences')
import labrad
import numpy as np
from PulseSequences.TimeRes_FFT import TimeResolved

recordTime = 1.0 #seconds
average = 10
freqSpan = 50.0 #Hz 
freqOffset = -625.0 #Hz, the offset between the counter clock and the rf synthesizer clock

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

freqs = np.arange(minFreq,maxFreq,freqRes)

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

pwr = np.zeros_like(freqs)
for i in range(average):
    print 'iteration {0} out of {1}'.format(i+1, average)
    pulser.reset_timetags()
    pulser.start_single()
    pulser.wait_sequence_done()
    pulser.stop_sequence()
    timetags = pulser.get_timetags().asarray
    print 'photons counted', timetags.size
    pwr += getFFTpwr(timetags)
    
pwr = pwr / float(average) #normalizing to the number of iterations
totalPower = np.sum(pwr)
#saving
dv.cd(['','QuickMeasurements','FFT'],True)
name = dv.new('FFT',[('Freq', 'Hz')], [('Power','Arb','Arb')] )
data = np.array(np.vstack((freqs,pwr)).transpose(), dtype = 'float')
dv.add_parameter('plotLive',True)
dv.add(data)
print 'Saved {}'.format(name)
print 'Total Power {}'.format(totalPower)
print 'DONE'