#plot the binned timetags
from constants import constants as c
import numpy as np
import matplotlib

from matplotlib import pyplot

f = np.load(c.bin_filename)
bins = f[:,0]
hist = f[:,1]
bins = bins*1e6 #plot time bins in microseconds
pyplot.plot(bins, hist)
pyplot.fill_between(bins[0:4200],0,hist[0:4200],color='#99ffff')
pyplot.fill_between(bins[4200:8685],0,hist[4200:8685],color='#ccffff')
pyplot.fill_between(bins[8685:9990],0,hist[8685:9990],color='#ff3333')
#pyplot.title('Branching Ratio ' + c.bin_filename)
#pyplot.xlabel(u'Time \265s')
bin_size = bins[1] - bins[0]
#pyplot.ylabel(u'Photons per bin of {} \265s'.format(bin_size))
pyplot.show()