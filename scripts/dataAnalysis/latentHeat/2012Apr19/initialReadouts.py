import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

meltingThreshold = 180
totalTraces = 5
binTime =250.0*10**-6
excludeStat = 0.05 #discard traces with fewer than this percentage of events i.e if melts once, don't plot
experiment = 'LatentHeat_no729_autocrystal'
datasets = ['2012Apr19_1647_06','2012Apr19_1648_25','2012Apr19_1649_33','2012Apr19_1651_16',
            '2012Apr19_1653_11', '2012Apr19_1655_13','2012Apr19_1657_09','2012Apr19_1659_25','2012Apr19_1702_19']

figure = pyplot.figure()
figure.clf()
pyplot.suptitle('')
initRead = []
delay_times = []


for datasetName in datasets:
    melted = 0
    crystal = 0
    data = []
    #getting parameters
    dv.cd(['','Experiments',experiment,datasetName])
    dv.open(1)
    print datasetName
    recordTime = dv.get_parameter('recordTime')
    binNumber = int(recordTime / binTime)
    binArray = binTime * numpy.arange(binNumber + 1)
    fluorMelted = numpy.zeros(binNumber)
    fluorCrystal = numpy.zeros(binNumber)
    initial_cooling = dv.get_parameter('initial_cooling')
    heat_delay = dv.get_parameter('heat_delay')
    axial_heat = dv.get_parameter('axial_heat')
    readout_delay = dv.get_parameter('readout_delay')
    delay_times.append(readout_delay * 10.**3)
    readout_delay = dv.get_parameter('readout_delay')
    readout_time = dv.get_parameter('readout_time')
    #readout range
    startReadout =  (initial_cooling + heat_delay + axial_heat + readout_delay ) #now in seconds
    stopReadout = startReadout + readout_time #now in seconds
    #data processing on the fly
    dv.cd(['','Experiments',experiment,datasetName,'timetags'])
    melted = 0
    for dataset in range(1,totalTraces+1):
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
    #if melted > excludeStat * totalTraces:
     #   fluorMelted = fluorMelted / float(melted)
     #   pyplot.plot(binArray[:-1],fluorMelted, label = 'Melted {0}, heating {1} ms'.format(datasetName,axial_heat/10.**3))
    if crystal > excludeStat * totalTraces:
        fluorCrystal = fluorCrystal / float(crystal)
        #pyplot.plot(binArray[:-1],fluorCrystal, label = 'Crystallized {0}, heating {1} ms'.format(datasetName,axial_heat/10.**3))
    data = [binArray[:-1], fluorCrystal] 
    beginRead = numpy.average(numpy.array(fluorCrystal[numpy.rint(startReadout/binTime)],fluorCrystal[numpy.rint(startReadout/binTime)+1]))#average of first two readout counts
    initRead.append(beginRead)
    numpy.savetxt(datasetName+'.csv',data,delimiter=",")
pyplot.plot(delay_times, initRead, '-o', label = 'initial Readout signal')
pyplot.legend()
pyplot.show()