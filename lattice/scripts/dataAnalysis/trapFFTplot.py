# for FFt measurements on 03/22/2012

import labrad
import numpy
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault
dv.cd(['','QuickMeasurements','FFT'])
FFTs = []

datasets = [689,687,685,661,676,678,681,683]
Comp_tilt = [40,30,20,13,0,-10,-20,-30]
for dataset in datasets:
    dv.open(int(dataset))
    #dv.open(645)
    data = dv.get().asarray
    freqs = data[:,0]
    counts = data[:,1]
    mx = numpy.max(counts)
    FFTs.append(mx)
print FFTs
figure = pyplot.figure()
figure.clf()
figure.suptitle('RF = 0 dBm')
pyplot.plot(Comp_tilt, FFTs, '-o')
pyplot.xlabel('Compensation tilt (V)')
pyplot.ylabel('FFT micromotion amplitude (arb)')
pyplot.show()