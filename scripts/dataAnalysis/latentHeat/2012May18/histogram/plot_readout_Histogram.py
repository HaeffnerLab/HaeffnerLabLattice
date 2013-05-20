import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot

totalTraces = 200

datasets = ['2012May18_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [174535,174755,175012,175234]] #heating time'
title = '2012May18 heating time' 
#atasets = ['2012May18_{0:=04}_{1:=02}'.format(x/100, x % 100) for x in [180659,181108,181449,181820,182122,182407,182637,182905,183134,183719]] #delay time
#title = '2012May18 delay time' 
refSigs = []
detectedCounts = [] #list of counts detected during readout

figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Histogram of readouts')

for datasetName in datasets:
    print 'Getting heating counts...'
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName])
    print dv.dir()
    datasetCounts = []
    dv.open(1)    
    initial_cooling = dv.get_parameter('initial_cooling')
    heat_delay = dv.get_parameter('heat_delay')
    axial_heat = dv.get_parameter('axial_heat')
    readout_delay = dv.get_parameter('readout_delay')
    readout_time = dv.get_parameter('readout_time')
    xtal_record = dv.get_parameter('xtal_record')
#    
    # readout range
    heatStart = (initial_cooling + heat_delay ) # / 10.0**6 #in seconds
    heatEnd = (initial_cooling + heat_delay +axial_heat ) 
    startReadout =  (axial_heat + initial_cooling + heat_delay + axial_heat + readout_delay ) 
    stopReadout = startReadout + readout_time 
    print datasetName, heatStart, heatEnd, startReadout, stopReadout
    print 'Heating time :', heatEnd - heatStart
    print 'Delay time :', readout_delay
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName,'timetags'])
        
    for dataset in range(1,totalTraces+1):
        dv.open(int(dataset))
        timetags = dv.get().asarray[:,0]
        countsReadout = numpy.count_nonzero((startReadout <= timetags) * (timetags <= stopReadout))
        countsReadout = countsReadout / float(readout_time) #now in counts/secz
        datasetCounts.append(countsReadout)
        detectedCounts.append(countsReadout)
    pyplot.hist(datasetCounts, 60, histtype = 'step', label = 'heating = {0} ms, delay = {1} ms'.format(1000 * axial_heat, 1000 * readout_delay))

print 'Done'
pyplot.hist(detectedCounts, 60, histtype = 'step', label = 'Total')
pyplot.xlabel('Counts / Sec')
pyplot.title(title)
pyplot.legend()
pyplot.show()