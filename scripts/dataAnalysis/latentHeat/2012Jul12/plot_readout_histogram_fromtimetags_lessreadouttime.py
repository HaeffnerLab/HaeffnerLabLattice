import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

totalTraces = 200
READOUT_TIME = 1e-3
date = '2012Jul12'; datasets = ['{0}_{1:=04}_{2:=02}'.format(date, x/100, x % 100) for x in [154705]] 
title = '{}'.format(date) 

figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Histogram of readouts')
totalCounts = numpy.array([])

def getPercentage(counts, threshold):
    below = numpy.count_nonzero(counts <= threshold) / float(counts.size)
    above = numpy.count_nonzero(counts > threshold) / float(counts.size)
    return (below, above)

for datasetName in datasets:
    print datasetName
    dv.cd(['','Experiments','LatentHeat_Global_Auto',date,datasetName])
    dv.open(4)
    axial_heat = dv.get_parameter('axial_heat')
    readout_delay = dv.get_parameter('readout_delay')
    start_readout = dv.get_parameter('startReadout')
    end_readout = start_readout + READOUT_TIME
    dv.open(1)
    data = dv.get().asarray
    iterations = data[:,0]
    timetags = data[:,1]
    iters,indices = numpy.unique(iterations, return_index=True) #finds the iterations, and positions of new iterations beginning
    split = numpy.split(timetags, indices[1:]) #timetags are split for each iteration
    readout = []
    for tags in split:
        counts = numpy.count_nonzero( (tags >= start_readout) * (tags <= end_readout) )
        counts = counts / (end_readout - start_readout)
        readout.append(counts)
    totalCounts = numpy.append(totalCounts, readout)
    pyplot.hist(readout, 60, histtype = 'step', label = 'heating = {0} ms, delay = {1} ms'.format(1000 * axial_heat, 1000 * readout_delay))

print 'Done'
pyplot.hist(totalCounts, 60, histtype = 'step', label = 'Total')
pyplot.xlim(xmin = 0)
pyplot.ylim(ymin = 0)
pyplot.xlabel('Counts / Sec')
pyplot.title(title)
pyplot.legend()
pyplot.show()