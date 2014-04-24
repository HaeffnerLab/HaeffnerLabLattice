from __future__ import division
import labrad
import numpy as np
from matplotlib import pyplot
import matplotlib
import lmfit

figure = pyplot.figure(1)
figure.clf()

time = np.load('time_2014_04_12.npy')
freq = np.load('freq_2014_04_12.npy')

bin_size = 200
number_of_bin = int(np.max(time)/bin_size)-1
print number_of_bin
freq = freq-np.average(freq)

freq_binned = []
freq_sd_array = []
time_binned = []

for i in range(0, number_of_bin+1):
    period = (i+1)*bin_size
    where = np.where((time>(i*bin_size))*(time<=((i+1)*bin_size)))
    freq_mean = np.average(freq[where])
    freq_sd = np.std(freq[where])
    freq_binned.append(freq_mean)
    freq_sd_array.append(freq_sd)
    time_binned.append((i+1)*bin_size)

np.save('time_binned_2014_04_12',time_binned)
np.save('freq_binned_2014_04_12',freq_binned)
np.save('freq_err_2014_04_12',freq_sd_array)
pyplot.plot(time_binned,freq_binned,'o')
pyplot.errorbar(time_binned,freq_binned, freq_sd_array)
pyplot.ylim([-1,1])

pyplot.show()
