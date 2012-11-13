import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

experiment = 'HeatingRateInvert'
totalTraces = 9
binTime =2yy0.0*10**-6
datasets = ['2012Feb23_1659_43']
            
figure = pyplot.figure()
figure.clf()
pyplot.suptitle('SQIP')
for datasetName in datasets:
    data = []
    #getting parameters
    dv.cd(['','Experiments',experiment,datasetName])
    dv.open(1)    
#    axial_heat = dv.get_parameter('axial_heat') / 1000.0 #now in ms
#    readout_delay = dv.get_parameter('readout_delay') / 1000.0 #now in ms
#    recordTime = dv.get_parameter('recordTime')
    recordTime = 150*10**-3
    #data processing on the fly
    binNumber = int(recordTime / binTime)
    binArray = binTime * numpy.arange(binNumber + 1)
    dv.cd(['','Experiments',experiment,datasetName,'timetags'])
    fluor = numpy.zeros(binNumber)
    for dataset in range(1,totalTraces+1):
        #print dataset
        dv.open(int(dataset))
        timetags = dv.get().asarray[:,0]
        newbinned = numpy.histogram(timetags, binArray )[0]
        fluor = fluor + newbinned
    pyplot.plot(binArray[:-1],fluor)#, label = '{0}, heating {1} ms'.format(datasetName,axial_heat))

pyplot.xlabel('Time (sec)')
pyplot.ylabel('Counts (arb)')
#pyplot.legend()
pyplot.show()