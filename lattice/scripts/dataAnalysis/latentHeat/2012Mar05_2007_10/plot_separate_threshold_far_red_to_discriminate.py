import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

meltingThreshold = 350
totalTraces = 100
binTime =250.0*10**-6
excludeStat = 0.05 #discard traces with fewer than this percentage of events i.e if melts once, don't plot
datasets = ['2012Mar05_2021_19', '2012Mar05_2034_11','2012Mar05_2007_10']

figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Separated Traces 40ms heating')


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
    global_off_start =  dv.get_parameter('global_off_start')
    readout_delay = dv.get_parameter('readout_delay')
    heat_time = dv.get_parameter('axial_heat')
    readout_delay = dv.get_parameter('readout_delay')
    shutter_delay = dv.get_parameter('shutter_delay')
    crystallize_delay = dv.get_parameter('crystallize_delay')
    #readout range
    startReadout =  0.300
    stopReadout = 0.400
    print datasetName, startReadout, stopReadout
    #data processing on the fly
    dv.cd(['','Experiments','LatentHeat_no729',datasetName,'timetags'])
    melted = 0
    for dataset in range(1,totalTraces+1):
        print dataset
        dv.open(int(dataset))
        timetags = dv.get().asarray[:,0]
        countsReadout = numpy.count_nonzero((startReadout <= timetags) * (timetags <= stopReadout))
        newbinned = numpy.histogram(timetags, binArray )[0]
        if countsReadout > meltingThreshold: #far red melted if fluorescence is higher
            fluorMelted += newbinned
            melted += 1
        else:
            fluorCrystal += newbinned
            crystal += 1
    #normalizing and excluding ones that don't have enough statistics
    if melted > excludeStat * totalTraces:
        fluorMelted = fluorMelted / float(melted)
        pyplot.plot(binArray[:-1],fluorMelted, label = 'Melted {0}, delay {1} ms'.format(datasetName,readout_delay / 10.**3))
    if crystal > excludeStat * totalTraces:
        fluorCrystal = fluorCrystal / float(crystal)
        pyplot.plot(binArray[:-1],fluorCrystal, label = 'Crystallized {0}, delay {1} ms'.format(datasetName,readout_delay / 10.**3))
        
pyplot.legend()
pyplot.show()