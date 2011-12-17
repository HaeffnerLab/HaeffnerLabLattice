import os; labradPath = os.environ.get('LABRADPATH') 
path = os.path.join(labradPath,'lattice/scripts')
import sys; sys.path.append(path)
import labrad; cxn = labrad.connect()
from scriptLibrary import paulsbox 
import numpy as np

centerFreq = 15.00*10**6
ptsAround = 1
recordTime = 0.5 #seconds
iterations = 1000
average = 1
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


freqs = centerFreq + np.arange(-ptsAround,ptsAround + 1) * freqRes
#def getFFTpwr(timetags):
#    fft = np.zeros_like(freqs, dtype = np.complex)
#    for k in range(freqs.size):
#        fft[k] = np.dot(timetags,np.exp(-1.j*2.0*np.pi*freqs[k]*timetags))
#        pwr = np.abs(fft)**2.0
#    return pwr

def getFFTpwr(timetags):
    mat = np.exp(-1.j*2.0*np.pi*np.outer(freqs, timetags))
    fft = mat.sum(axis=1)
    pwr = np.abs(fft)**2.0
    pwr = pwr / timetags.size 
    return pwr

dv.cd(['','QuickMeasurements','FFTlive'],True)
dv.new('FFT',[('time', 'arb')], [('Power','Arb','Arb')] )
for i in range(iterations):
    pwr = np.zeros_like(freqs)
    for j in range(average):
        trfpga.perform_time_resolved_measurement()
        trigger.trigger('PaulBox')
        timetags = trfpga.get_result_of_measurement().asarray
        pwr += getFFTpwr(timetags)
    pwr = pwr.sum() #find the total power across the frequencies 
    dv.add([i,pwr])
    print i,pwr
print 'DONE'


