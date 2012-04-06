import numpy as np
N = 1000

signal = np.random.randint(0,2,N)
#signal = np.ones(N)
fft = np.fft.fft(signal)
one =  np.sum(signal**2) #sane as timetags.size
two = np.sum(np.abs(fft)**2)
print one / (two / signal.size)


timeResolution = (10e-9)
recordTime = signal.size * timeResolution

maxFreq = 1 / timeResolution
freqs = np.fft.fftfreq(N, timeResolution)[1:100]

timetags = np.array(signal.nonzero()) * timeResolution

def getFFTpwr(timetags):
    mat = np.exp(-1.j*2.0*np.pi*np.outer(freqs, timetags))
    fft = mat.sum(axis=1)
    pwr = np.abs(fft)**2.0 
    if timetags.size > 0:
        pwr = pwr / (N * timetags.size)
    else:
        pwr = np.zeros_like(freqs)
    del(mat,fft)
    return pwr

timetagPWR = np.sum(getFFTpwr(timetags))
print timetagPWR

#frequencies are not the complete domain
#timetags.size is not N