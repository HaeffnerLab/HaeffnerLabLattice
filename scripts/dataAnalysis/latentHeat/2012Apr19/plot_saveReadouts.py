import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot

meltingThreshold = 180
totalTraces = 50
binTime =250.0*10**-6
excludeStat = 0.05 #discard traces with fewer than this percentage of events i.e if melts once, don't plot
experiment = 'LatentHeat_no729_autocrystal'
#datasets = ['2012Apr19_1636_17','2012Apr19_1639_12','2012Apr19_1637_26','2012Apr19_1640_40','2012Apr19_1643_10','2012Apr19_1645_06'] #'10ions RF -3.5dBm', 225, 50
#info in the format, [(label, melting threshold, totalTraces, list of datasets),...]
info = [
       ('10ions RF -3.5dBm', 225, 50, ['2012Apr19_1647_06','2012Apr19_1648_25','2012Apr19_1649_33','2012Apr19_1651_16',
               '2012Apr19_1653_11', '2012Apr19_1655_13','2012Apr19_1657_09','2012Apr19_1659_25','2012Apr19_1702_19']),
       ('10ions RF -4.2dBm', 187, 50, ['2012Apr19_1719_25','2012Apr19_1720_35','2012Apr19_1722_24','2012Apr19_1723_53',
                '2012Apr19_1725_52','2012Apr19_1728_00','2012Apr19_1730_08']),
       ('10ions RF -5.0dBm', 200, 50, ['2012Apr19_1758_21','2012Apr19_1759_27','2012Apr19_1800_45','2012Apr19_1804_23',
                '2012Apr19_1801_55','2012Apr19_1806_23']),
       ('10ions RF -7.0dBm (close to zigzag)', 180, 50, ['2012Apr19_1816_52','2012Apr19_1822_59','2012Apr19_1824_03','2012Apr19_1817_56','2012Apr19_1818_55',
                 '2012Apr19_1819_59','2012Apr19_1821_11']),
       ('15ions RF -3.5dBm', 250, 50, ['2012Apr19_1944_39','2012Apr19_1956_00','2012Apr19_1954_34','2012Apr19_1647_06','2012Apr19_1945_56',
                '2012Apr19_1947_48','2012Apr19_1950_02','2012Apr19_1951_54']),
       ('15ions RF -7.0dBm, zigzag', 250, 50, ['2012Apr19_2043_39','2012Apr19_2051_40','2012Apr19_2053_11','2012Apr19_2044_45',
                '2012Apr19_2046_42','2012Apr19_2054_46','2012Apr19_2048_54']),
       ] 

figure = pyplot.figure()
figure.clf()
pyplot.suptitle('')
initRead = []

for i in range(len(info)):
    #label = info[i][0]
    meltingThreshold = info[i][1]
    totalTraces = info[i][2]
    datasets = info[i][3]
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
            pyplot.plot(binArray[:-1],fluorCrystal, label = 'Crystallized {0}, heat {1} ms'.format(datasetName,axial_heat/10.**3))
        data = [binArray[:-1], fluorCrystal] 
        #rint = numpy.rint
        dataRead = [binArray[rint(startReadout/binTime):rint(stopReadout/binTime)], fluorCrystal[rint(startReadout/binTime):rint(stopReadout/binTime)]]
        numpy.savetxt(datasetName+'.csv',dataRead,delimiter=",")
    pyplot.legend()
    pyplot.show()
print 'DONE'