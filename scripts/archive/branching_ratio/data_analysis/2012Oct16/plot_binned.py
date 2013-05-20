#plot the binned timetags
import numpy as np
import matplotlib

from matplotlib import pyplot
binned_file = '00001 - Timetags 2012Oct16_2036_59_binned.npy'
f = np.load(binned_file)
bins = f[:,0]
hist = f[:,1]
bins = bins*1e6 #plot time bins in microseconds
pyplot.plot(bins, hist)
pyplot.title('Branching Ratio ' + binned_file)
pyplot.xlabel(u'Time \265s')
pyplot.ylabel('Photons per bin of {}s'.format(bins.size))
pyplot.show()