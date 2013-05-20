import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot

meltingThreshold = 2500
totalTraces = 30
binTime =500.0*10**-6
excludeStat = 0.05 #discard traces with fewer than this percentage of events i.e if melts once, don't plot
experiment = 'LatentHeat_no729_autocrystal'
datasets = ['2012Mar08_1920_06', '2012Mar08_1921_47', '2012Mar08_1926_43']

#['2012Mar08_1918_28', '2012Mar08_1920_06','2012Mar08_1922_59','2012Mar08_1919_12',
 #          '2012Mar08_1921_47','2012Mar08_1920_53','2012Mar08_1924_11','2012Mar08_1926_43']

figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Separated Traces')


for datasetName in datasets:
    melted = 0
    crystal = 0
    #getting parameters
    dv.cd(['','Experiments',experiment,datasetName])
    dv.open(1)
    recordTime = dv.get_parameter('recordTime')
    binNumber = int(recordTime / binTime)
    binArray = binTime * numpy.arange(binNumber + 1)
    fluorMelted = numpy.zeros(binNumber)
    fluorCrystal = numpy.zeros(binNumber)
    initial_cooling = dv.get_parameter('initial_cooling')
    heat_delay = dv.get_parameter('heat_delay')
    axial_heat = dv.get_parameter('axial_heat')
    readout_delay = dv.get_parameter('readout_delay')
    readout_time = dv.get_parameter('readout_time')
    #readout range
    startReadout =  (initial_cooling + heat_delay + axial_heat + readout_delay ) / 10.0**6 #now in seconds
    stopReadout = startReadout + readout_time / 10.0**6 #now in seconds
    #data processing on the fly
    dv.cd(['','Experiments',experiment,datasetName,'timetags'])
    melted = 0
    for dataset in range(1,totalTraces+1):
        print dataset
        dv.open(int(dataset))
        timetags = dv.get().asarray[:,0]
        countsReadout = numpy.count_nonzero((startReadout <= timetags) * (timetags <= stopReadout))
        newbinned = numpy.histogram(timetags, binArray )[0]
        if countsReadout < meltingThreshold:
            fluorMelted += newbinned
            melted += 1
        else:
            fluorCrystal += newbinned
            crystal += 1
    #normalizing and excluding ones that don't have enough statistics
    if melted > excludeStat * totalTraces:
        fluorMelted = fluorMelted / float(melted)
        pyplot.plot(binArray[:-1],fluorMelted, label = 'Melted {0}, heating {1} ms'.format(datasetName,axial_heat/10.**3))
    if crystal > excludeStat * totalTraces:
        fluorCrystal = fluorCrystal / float(crystal)
        pyplot.plot(binArray[:-1],fluorCrystal, label = 'Crystallized {0}, heating {1} ms'.format(datasetName,axial_heat/10.**3))
        
pyplot.legend()
pyplot.show()