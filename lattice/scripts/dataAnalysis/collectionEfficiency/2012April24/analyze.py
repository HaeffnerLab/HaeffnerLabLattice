resource.getrlimit(resource.RLIMIT_NOFILE)=

import numpy
import labrad
import makeplot

def sliceArr(arr, start, duration, cyclenumber = 1, cycleduration = 0 ):
    '''Takes a numpy array arr, and returns a new array that consists of all elements between start and start + duration modulo the start time
    If cyclenumber and cycleduration are provided, the array will consist of additional slices taken between start and 
    start + duration each offset by a cycleduration. The additional elements will added modulo the start time of their respective cycle'''
    starts = [start + i*cycleduration for i in range(cyclenumber)]
    criterion = reduce(numpy.logical_or, [(start <= arr) & (arr <=  start + duration) for start in starts])
    result = arr[criterion]
    if cycleduration == 0:
        result = numpy.mod(result, start)
    else:
        result = numpy.mod(result - start, cycleduration)
    return result

cxn = labrad.connect()
dv = cxn.data_vault

experiment = 'collectionEfficiency'
#dataset = '2012Apr24_1702_39'
#dataset = '2012Apr24_1629_24'
dataset = '2012Apr24_1625_39'
iterationsCycle = 250
iterDelay = 1.0e-6
exciteP = 1.0e-6
finalDelay = 5.0e-6
repumpD = 5.0e-6
repumpDelay = 1.0e-7
dopplerCooling = 0.1

dv.cd(['', 'Experiments', experiment, dataset, 'timetags'])
repeations = len(dv.dir()[1])

binTime = 40.0*10**-9 #fpga resolution

cycleTime = repumpD + repumpDelay + exciteP + finalDelay
binNumber = int(cycleTime / binTime)
bins = binTime * numpy.arange(binNumber + 1)
binned = numpy.zeros(binNumber)

for i in range(1, repeations + 1):
    print 'opening', i
    dv.open(i)
    timetags = dv.get().asarray
    sliced = sliceArr(timetags, start = dopplerCooling + iterDelay, duration = cycleTime, cyclenumber = iterationsCycle,  cycleduration = cycleTime)
    binned += numpy.histogram(sliced,  bins)[0]
    
numpy.savez('{}binning'.format(dataset), binned = binned, bins = bins)
makeplot.makePlot(bins, binned)