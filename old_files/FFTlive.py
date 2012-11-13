import os; labradPath = os.environ.get('LABRADPATH') 
path = os.path.join(labradPath,'lattice/scripts')
import sys; sys.path.append(path)
import labrad; cxn = labrad.connect()
from scriptLibrary import paulsbox 
import numpy as np

centerFreq = 14998866#15.00*10**6
ptsAround = 4
recordTime = 0.5 #seconds
iterations = 50
average = 3
#program pulse sequence for triggering time resolved
pboxDict = {
            'sequence':'TimeResolvedTrigger.py',
            'nothing':1,
            }
paulsbox.program(cxn.paul_box, pboxDict)
trfpga = cxn.timeresolvedfpga
trigger = cxn.trigger
trfpga.set_time_length(recordTime)
timeResolution = float(trfpga.get_resolution())
freqRes = 1.0 / recordTime
dv = cxn.data_vault


freqs = centerFreq + np.arange(-ptsAround,ptsAround + 1) * freqRes

def getFFTpwr(timetags):
    mat = np.exp(-1.j*2.0*np.pi*np.outer(freqs, timetags))
    fft = mat.sum(axis=1)
    pwr = np.abs(fft)**2.0
    pwr = pwr / timetags.size
    del(mat,fft)
    return pwr

import time

dv.cd(['','QuickMeasurements','FFTlive'],True)
dv.new('FFT',[('time', 'arb')], [('Power','Arb','Arb')] )
for i in range(iterations):
    pwr = np.zeros_like(freqs)
    for j in range(average):
        trfpga.perform_time_resolved_measurement()
        time.sleep(.1)
        trigger.trigger('PaulBox')
        timetags = trfpga.get_result_of_measurement().asarray
        pwr += getFFTpwr(timetags)
    pwr = pwr.sum() #find the total power across the frequencies 
    dv.add([i,pwr])
    print i,pwr
print 'DONE'


