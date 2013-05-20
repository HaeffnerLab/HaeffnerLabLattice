import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot

experiment = 'LatentHeat_no729_autocrystal'
totalTraces = 30
binTime =250.0*10**-6
datasets = ['2012Mar08_1928_29', '2012Mar08_1929_19', '2012Mar08_1930_00', '2012Mar08_1931_04','2012Mar08_1932_12'] # 95 ms heating

#['2012Mar08_1934_58', '2012Mar08_1935_44', '2012Mar08_1936_35', '2012Mar08_1937_38','2012Mar08_1938_36'] # 135 ms heating
#['2012Mar08_1928_29', '2012Mar08_1929_19', '2012Mar08_1930_00', '2012Mar08_1931_04','2012Mar08_1932_12'] # 95 ms heating


figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Far Blue Heating 6 ions')
for datasetName in datasets:
    #getting parameters
    dv.cd(['','Experiments',experiment,datasetName])
    dv.open(1)    
    axial_heat = dv.get_parameter('axial_heat') / 1000.0 #now in ms
    readout_delay = dv.get_parameter('readout_delay') / 1000.0 #now in ms
    recordTime = dv.get_parameter('recordTime')
    #data processing on the fly
    binNumber = int(recordTime / binTime)
    binArray = binTime * numpy.arange(binNumber + 1)
    dv.cd(['','Experiments',experiment,datasetName,'timetags'])
    fluor = numpy.zeros(binNumber)
    for dataset in range(1,totalTraces+1):
        print dataset
        dv.open(int(dataset))
        timetags = dv.get().asarray[:,0]
        newbinned = numpy.histogram(timetags, binArray )[0]
        fluor = fluor + newbinned
    pyplot.plot(binArray[:-1],fluor, label = '{0}, heating {1} ms, delay time {2} ms'.format(datasetName,axial_heat,readout_delay))

pyplot.xlabel('Time (sec)')
pyplot.ylabel('Counts (arb)')
pyplot.legend()
pyplot.show()