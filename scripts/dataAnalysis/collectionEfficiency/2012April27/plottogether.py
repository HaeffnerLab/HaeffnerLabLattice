import numpy as np
import matplotlib

from matplotlib import pyplot

#datasets = [
#            ('397: -12dBm 866: 0 deg', '2012Apr27_1817_45binning.npz'),
#            ('397: -12dBm 866: +22.5deg','2012Apr27_1849_26binning.npz'),
#            ('397: -12dBm 866: +45.0deg','2012Apr27_1918_55binning.npz'),
#            ('397: -4.0dBm 866: 0 deg','2012Apr27_1949_31binning.npz'),
#            ]

datasets= [
           ('397: -12.0dBm, B = 2amps','2012Apr27_1742_15binning.npz'),
           ('397: -12dBm,   B = 0',  '2012Apr27_1650_23binning.npz'),
           ]
pyplot.figure()
for data in datasets:
    label,name = data
    f = np.load(name)
    bins = f['bins']
    binned = f['binned']
    pyplot.plot(bins[0:-1],binned, label = label)
ax = pyplot.gca()
ax.ticklabel_format(style = 'sci', scilimits = (0,0), axis = 'x')
pyplot.xlabel('Sec')
pyplot.ylabel('Counts/Sec')
pyplot.legend()
pyplot.show()