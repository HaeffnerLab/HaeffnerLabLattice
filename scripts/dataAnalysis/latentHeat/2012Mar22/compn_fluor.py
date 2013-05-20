# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 13:09:42 2012

"""

import numpy
import labrad
cxn = labrad.connect()
import matplotlib

from matplotlib import pyplot

datasets = ['2012Mar22_2040_07','2012Mar22_2017_29','2012Mar22_2014_37','2012Mar22_1946_14','2012Mar22_1925_02']
#DIRECTORY = ['','Experiments','LatentHeat',datasetName,'timetags']
dv = cxn.data_vault


recordTime = .50 #seconds
binTime =250*10**-6
totalTraces = 100
binNumber = int(recordTime / binTime)
binArray = binTime * numpy.arange(binNumber + 1)
meltedFluor = numpy.zeros(binNumber)
notmeltedFluor = numpy.zeros(binNumber)

figure = pyplot.figure()
figure.clf()
pyplot.suptitle('heating time = 55 ms')
tilt = -30
for datasetName in datasets:
    print datasetName
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName])
    dv.open(1)    
    axial_heat = dv.get_parameter('axial_heat') / 1000.0 #now in ms
    #recordTime = dv.get_parameter('recordTime')
    binNumber = int(recordTime / binTime)
    binArray = binTime * numpy.arange(binNumber + 1)
    dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName,'timetags'])
    fluor = numpy.zeros(binNumber)
    for dataset in range(1,totalTraces+1):
        #print dataset
        dv.open(int(dataset))
        timetags = dv.get().asarray[:,0]
        newbinned = numpy.histogram(timetags, binArray )[0]
        fluor = fluor + newbinned
    pyplot.plot(binArray[:-1],fluor, label = 'Tilt = {0} V'.format(tilt))
    tilt = tilt + 15
pyplot.legend()
pyplot.xlabel('time (seconds)')
pyplot.ylabel('Fluorescence (kCounts)')
pyplot.show()
