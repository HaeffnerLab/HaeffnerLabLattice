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
pyplot.title('Branching Ratio ' + c.bin_filename)
pyplot.xlabel(u'Time \265s')
pyplot.ylabel('Photons per bin of {}s'.format(bins.size))
pyplot.show()