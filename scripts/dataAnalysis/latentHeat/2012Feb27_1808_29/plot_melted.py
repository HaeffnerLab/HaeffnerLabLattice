import numpy

datasetName = '2012Feb27_1808_29'
meltedCamera = [2,3,7,8,9,15,16,20,21,24,25,26,27,28,29,30,31,32,36,37,38,40,
          41,45,46,57,58,60,61,62,63,66,69,71,72,73,74,75,77,78,81,82,83,84,
          87,90,93,94,95,98,100]
melted = set(101 - numpy.array(meltedCamera)) #order is reversed for saving on camera

DIRECTORY = ['','Experiments','LatentHeat',datasetName,'timetags']

notMelted = set(range(1,100)) - melted

import labrad
cxn = labrad.connect()
dv = cxn.data_vault
dv.cd(DIRECTORY)
import matplotlib

from matplotlib import pyplot

#data processing on the fly
recordTime = .50 #seconds
binTime =250.0*10**-6
binNumber = int(recordTime / binTime)
binArray = binTime * numpy.arange(binNumber + 1)
meltedFluor = numpy.zeros(binNumber)
notmeltedFluor = numpy.zeros(binNumber)

for dataset in notMelted:
    print dataset
    dv.open(int(dataset))
    timetags = dv.get().asarray[:,0]
    newbinned = numpy.histogram(timetags, binArray )[0]
    notmeltedFluor = notmeltedFluor + newbinned

for dataset in melted:
    print dataset
    dv.open(int(dataset))
    timetags = dv.get().asarray[:,0]
    newbinned = numpy.histogram(timetags, binArray )[0]
    meltedFluor = meltedFluor + newbinned
    
figure = pyplot.figure()
figure.clf()
pyplot.suptitle(datasetName)
pyplot.plot(binArray[:-1],notmeltedFluor, 'r',label = 'not melted')
pyplot.plot(binArray[:-1],meltedFluor, 'b',label = 'melted')
pyplot.xlabel('time (seconds)')
pyplot.ylabel('Fluorescence (kCounts)')
pyplot.legend()

pyplot.show()