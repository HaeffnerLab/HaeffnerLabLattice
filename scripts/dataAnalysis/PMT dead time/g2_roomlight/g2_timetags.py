from matplotlib import pyplot
import labrad
import numpy as np
from scripts.scriptLibrary.correlations import correlator

cxn = labrad.connect()
dv = cxn.data_vault
dv.cd(['','SimpleMeasurements','Timetags','2012Dec11','1359_49'])

measurement_time = 0.2 #sec
resolution = 10e-9
max_k = 100
g2 = np.zeros(max_k)
range_max = 2000

for i in range(1,range_max):
    print 'iteartion', i
    dv.open(i)
    timetags = dv.get().asarray
    timetags = timetags.transpose()[1]
    positions = np.round(timetags / resolution, 0)
    positions = np.array(positions, dtype = np.int)
    counts = np.zeros(measurement_time / resolution)
    counts[positions] = 1
    kk, g2_new =  correlator.g2(counts, max_k)
    g2 += g2_new

g2 = g2 / float(range_max)

np.save('g2', g2)

pyplot.figure()
pyplot.bar(kk, g2)
pyplot.show()