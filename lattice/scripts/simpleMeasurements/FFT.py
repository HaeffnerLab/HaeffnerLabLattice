import os; labradPath = os.environ.get('LABRADPATH') 
path = os.path.join(labradPath,'lattice/scripts')
import sys; sys.path.append(path)
import labrad; cxn = labrad.connect()
from scriptLibrary import paulsbox 
import numpy as np

minFreq = 0.499*10**6 #Hz
maxFreq = 0.501*10**6
recordTime = 0.5 #seconds
average = 5
saveFFT = True
#program pulse sequence for triggering time resolved
pboxDict = {
            'sequence':'TimeResolvedTrigger.py',
            'nothing':1,
            }
paulsbox.program(cxn.paul_box, pboxDict)
trfpga = cxn.timeresolvedfpga
dp = cxn.dataprocessor
trigger = cxn.trigger
trfpga.set_time_length(recordTime)
timeResolution = float(trfpga.get_resolution())
freqRes = 1.0 / recordTime
dv = cxn.data_vault


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
    trfpga.perform_time_resolved_measurement()
    trigger.trigger('PaulBox')
    timetags = trfpga.get_result_of_measurement().asarray
    pwr += getFFTpwr(timetags)
if saveFFT:
    dv.cd(['','QuickMeasurements','FFT'],True)
    dv.new('FFT',[('Freq', 'Hz')], [('Power','Arb','Arb')] )
    data = np.array(np.vstack((freqs,pwr)).transpose(), dtype = 'float')
    dv.add(data)
print 'DONE'