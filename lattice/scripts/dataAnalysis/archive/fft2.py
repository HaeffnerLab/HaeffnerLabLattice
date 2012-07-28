import labrad
import numpy as np
cxn = labrad.connect()
dv = cxn.data_vault
dv.cd(['','Experiments','LatentHeat_no729_autocrystal','2012Mar08_1919_12'])
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

minFreq = 1504.0*10**3 #Hz
maxFreq = 1507.0*10**3 #Hz
dv.open(1) 
recordTime = np.float(dv.get_parameter('recordTime'))
#recordTime = 0.42 #seconds
freqRes = 1.0 / recordTime

freqs = np.arange(minFreq,maxFreq,freqRes)

def getFFTpwr(timetags):
    mat = np.exp(-1.j*2.0*np.pi*np.outer(freqs, timetags))
    fft = mat.sum(axis=1)
    pwr = np.abs(fft)**2.0
    pwr = pwr / timetags.size
    del(mat,fft)
    return pwr

dv.cd(['','Experiments','LatentHeat_no729_autocrystal','2012Mar08_1919_12','timetags'])
pwr = np.zeros_like(freqs)
for j in range(1,3):
    print 'processing', j
    dv.open(j)
    timetags = dv.get().asarray
    pwr += getFFTpwr(timetags)

figure = pyplot.figure()
figure.clf()
pyplot.plot(freqs, pwr)
pyplot.show()
