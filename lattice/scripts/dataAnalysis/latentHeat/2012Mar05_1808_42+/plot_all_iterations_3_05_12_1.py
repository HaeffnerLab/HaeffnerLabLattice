import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot


totalTraces = 100
binTime =250.0*10**-6
datasets = ['2012Mar05_1808_42', '2012Mar05_1814_52', '2012Mar05_1828_23', '2012Mar05_1834_31']

figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Far Blue Heating')
for datasetName in datasets:
    #getting parameters
    dv.cd(['','Experiments','LatentHeat_no729',datasetName])
    dv.open(1)    
    axial_heat = dv.get_parameter('axial_heat') / 1000.0 #now in ms
    recordTime = dv.get_parameter('recordTime')
    #data processing on the fly
    binNumber = int(recordTime / binTime)
    binArray = binTime * numpy.arange(binNumber + 1)
    dv.cd(['','Experiments','LatentHeat_no729',datasetName,'timetags'])
    fluor = numpy.zeros(binNumber)
    for dataset in range(1,totalTraces+1):
        print dataset
        dv.open(int(dataset))
        timetags = dv.get().asarray[:,0]
        newbinned = numpy.histogram(timetags, binArray )[0]
        fluor = fluor + newbinned
    pyplot.plot(binArray[:-1],fluor, label = '{0}, heating {1} ms'.format(datasetName,axial_heat))
pyplot.legend()
pyplot.show()