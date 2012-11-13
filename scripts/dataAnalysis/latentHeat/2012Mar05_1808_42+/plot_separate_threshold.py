import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

meltingThreshold = 1200
totalTraces = 100
binTime =250.0*10**-6
excludeStat = 0.05 #discard traces with fewer than this percentage of events i.e if melts once, don't plot
datasets = ['2012Mar05_1808_42', '2012Mar05_1814_52', '2012Mar05_1828_23', '2012Mar05_1834_31']

figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Separated Traces')


for datasetName in datasets:
    melted = 0
    crystal = 0
    #getting parameters
    dv.cd(['','Experiments','LatentHeat_no729',datasetName])
    dv.open(1)
    recordTime = dv.get_parameter('recordTime')
    binNumber = int(recordTime / binTime)
    binArray = binTime * numpy.arange(binNumber + 1)
    fluorMelted = numpy.zeros(binNumber)
    fluorCrystal = numpy.zeros(binNumber)
    axial_heat = dv.get_parameter('axial_heat') / 1000.0 #now in ms
    global_off_start =  dv.get_parameter('global_off_start')
    global_off_time = dv.get_parameter('global_off_time')
    shutter_delay = dv.get_parameter('shutter_delay')
    crystallize_delay = dv.get_parameter('crystallize_delay')
    #readout range
    startReadout =  (global_off_start + global_off_time) / 10.0**6 #now in seconds
    stopReadout = startReadout + (shutter_delay + crystallize_delay) / 10.0**6 #now in seconds
    #data processing on the fly
    dv.cd(['','Experiments','LatentHeat_no729',datasetName,'timetags'])
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
        pyplot.plot(binArray[:-1],fluorMelted, label = 'Melted {0}, heating {1} ms'.format(datasetName,axial_heat))
    if crystal > excludeStat * totalTraces:
        fluorCrystal = fluorCrystal / float(crystal)
        pyplot.plot(binArray[:-1],fluorCrystal, label = 'Crystallized {0}, heating {1} ms'.format(datasetName,axial_heat))
        
pyplot.legend()
pyplot.show()