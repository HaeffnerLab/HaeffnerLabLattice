import labrad
import numpy
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

#change directory
datasets = [182953, 183541, 184007, 184435, 184832]
detuning = [0, 250, 500, 750, 1000]
names = ["2012May16_{0:04d}_{1:02d}".format(x / 100, x % 100) for x in datasets]

figure = pyplot.figure()
for i,name in enumerate(names):
    dv.cd(['','Experiments','pulsedScanAxialPower',name])
    dv.open(2)
    data = dv.get().asarray
    x = data[:,0]
    y = data[:,1]
    pyplot.plot(x, y, label = "{0} Detuning = +{1}MHz".format(name, detuning[i]))


figure.suptitle('Axial Power Saturation')
pyplot.legend()
pyplot.xlabel( 'AO Power, dBm')
pyplot.ylabel('Count Rate, Counts / Sec')
pyplot.show()
