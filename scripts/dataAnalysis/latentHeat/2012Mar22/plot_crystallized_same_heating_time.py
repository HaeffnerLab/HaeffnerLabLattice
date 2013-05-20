import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot

meltingThreshold = 4000 
totalTraces = 100
datasets =  ['2012Mar22_2040_07','2012Mar22_2017_29','2012Mar22_2014_37','2012Mar22_1946_14','2012Mar22_1925_02']

detectedCounts = [] #list of counts detected during readout

figure = pyplot.figure()
figure.clf()
title = 'heating time: 55 ms (only initially crystallized plotted)'
pyplot.suptitle(title)

heat_times = []
recordTime = .50 #seconds
binTime =250*10**-6
totalTraces = 100
binNumber = int(recordTime / binTime)
binArray = binTime * numpy.arange(binNumber + 1)
tilt = -30 

for datasetName in datasets:
    refs = 0
    #getting parameters
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName])
    dv.open(1)    
    initial_cooling = dv.get_parameter('initial_cooling')
    heat_delay = dv.get_parameter('heat_delay')
    axial_heat = dv.get_parameter('axial_heat')
    heat_times.append(axial_heat * 10.**3)
    axial_heat = dv.get_parameter('axial_heat')
    readout_delay = dv.get_parameter('readout_delay')
    readout_time = dv.get_parameter('readout_time')
    xtal_record = dv.get_parameter('xtal_record')
   
    #readout range
    heatStart = (initial_cooling + heat_delay ) #in seconds
    heatEnd = (initial_cooling + heat_delay +axial_heat ) #in seconds
    startReadout =  (initial_cooling + heat_delay + axial_heat + readout_delay )  #in seconds
    stopReadout = startReadout + readout_time # in seconds
    print datasetName, startReadout, stopReadout, heatStart, heatEnd
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName,'timetags'])
    fluor = numpy.zeros(binNumber)
    for dataset in range(1,totalTraces+1):
        dv.open(int(dataset))
        timetags = dv.get().asarray[:,0]
        countsReadout = numpy.count_nonzero((startReadout <= timetags) * (timetags <= stopReadout))
        if countsReadout > meltingThreshold: # melting is less counts
            newbinned = numpy.histogram(timetags, binArray )[0]
            fluor = fluor + newbinned
    pyplot.plot(binArray[:-1],fluor, label = 'Tilt = {0} V'.format(tilt))
    tilt = tilt + 15

pyplot.legend()
pyplot.xlabel('time (seconds)')
pyplot.ylabel('Fluorescence (kCounts)')
pyplot.show()
