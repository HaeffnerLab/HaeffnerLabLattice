import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

totalTraces = 200
#date = '2012Jul03'; datasets = ['{0}_{1:=04}_{2:=02}'.format(date, x/100, x % 100) for x in [211021, 211322, 211916, 212831]] 
date = '2012Jul04';datasets = ['{0}_{1:=04}_{2:=02}'.format(date, x/100, x % 100) for x in [82928, 85057, 91856]]  
title = '{} testing'.format(date) 

totalCounts = numpy.zeros(totalTraces)
figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Histogram of readouts')
totalCounts = numpy.array([])

def getPercentage(counts, threshold):
    below = numpy.count_nonzero(counts <= threshold) / float(counts.size)
    above = numpy.count_nonzero(counts > threshold) / float(counts.size)
    return (below, above)

for datasetName in datasets:
    dv.cd(['','Experiments','LatentHeat_Global_Auto',date,datasetName])
    print datasetName
    dv.open(4)
    axial_heat = dv.get_parameter('axial_heat')
    readout_delay = dv.get_parameter('readout_delay')
    dv.open(2)    
    data = dv.get().asarray
    readout = data.transpose()[1]
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