import numpy as np
import matplotlib

from matplotlib import pyplot

#dataset = '1555_40' #slope
#dataset = '1553_55' #top of peak
#dataset = '1558_44' #ion oscllating axially
#dataset = '1602_25' #ion oscillating radially

datasets = ['1555_40', '1558_44']
pyplot.figure()
for num, dataset in enumerate(datasets):
    total_fft = np.load(dataset + '.npy')
    fft_freq = np.arange(total_fft.size)
    max_args = total_fft.argsort()[-10000:] 
    max_freqs =  fft_freq[max_args]
    max_freqs.sort()
    max_freqs = max_freqs[np.where(total_fft[max_freqs] > 7000.0)] #cutoff heigh-wise
    differences = np.ediff1d(max_freqs)
    max_freqs = max_freqs[np.where(differences > 100.0)] #where differences are more than 100 hz
    print 'maximum frequencies'
    print max_freqs / 1e6
    print 'plotting'
    offset = num * 30000
    pyplot.plot(fft_freq[max_args] / 1e6, offset + total_fft[max_args] , 'o', markersize = 2.0)
pyplot.xlabel("Frequency MHz")
pyplot.ylabel("FFT Peak (Arb)")
pyplot.show()