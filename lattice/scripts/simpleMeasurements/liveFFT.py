import os; labradPath = os.environ.get('LABRADPATH') 
path = os.path.join(labradPath,'lattice/scripts')
import sys; sys.path.append(path)
import labrad; cxn = labrad.connect()
from scriptLibrary import paulsbox 
import numpy as np

minFreq = 14.99*10**6 #Hz
maxFreq = 15.00*10**6 #Hz
freqRes = 3 #Hz
recordTime = 0.5 #seconds
saveFFT = True
#program pulse sequence for triggering time resolved
pboxDict = {
            'sequence':'TimeResolvedTrigger.py',
            'nothing':1,
            }
paulsbox.program(cxn.paul_box, pboxDict)
freqs = np.arange(minFreq,maxFreq,freqRes)
trfpga = cxn.timeresolvedfpga
dp = cxn.dataprocessor
trigger = cxn.trigger
trfpga.set_time_length(recordTime)
timeResolution = trfpga.get_resolution()
dv = cxn.data_vault

def getFFTpwr(timetags):
    fft = np.zeros_like(freqs, dtype = np.complex)
    for k in range(freqs.size):
        fft[k] = np.dot(timetags,np.exp(-1.j*2*np.pi*freqs[k]*timetags))
        pwr = np.abs(fft)**2
    return pwr
    

trfpga.perform_time_resolved_measurement()
trigger.trigger('PaulBox')
timetags = trfpga.get_result_of_measurement().asarray
pwr = getFFTpwr(timetags)
if saveFFT:
    dv.cd(['','QuickMeasurements','FFT'],True)
    dv.new('FFT',[('Freq', 'Hz')], [('Power','Arb','Arb')] )
    data = np.vstack((freqs,pwr)).transpose()
    dv.add(data)
print 'DONE'


