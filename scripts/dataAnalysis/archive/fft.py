import labrad
import numpy as np
cxn = labrad.connect()
dv = cxn.data_vault
dv.cd(['','Experiments','EnergyTransportv2','2011Dec15_2056_11','timetags'])
import matplotlib

from matplotlib import pyplot

minFreq = 0.0*10**3 #Hz
maxFreq = 5.0*10**3 #Hz
recordTime = 0.3 #seconds
freqRes = 1.0 / recordTime

freqs = np.arange(minFreq,maxFreq,freqRes)

def getFFTpwr(timetags):
    mat = np.exp(-1.j*2.0*np.pi*np.outer(freqs, timetags))
    fft = mat.sum(axis=1)
    pwr = np.abs(fft)**2.0
    pwr = pwr / timetags.size
    del(mat,fft)
    return pwr

pwr = np.zeros_like(freqs)
for j in range(1,100):
    print 'processing', j
    dv.open(j)
    timetags = dv.get().asarray
    pwr += getFFTpwr(timetags)

figure = pyplot.figure()
figure.clf()
pyplot.plot(freqs, pwr)
pyplot.show()
