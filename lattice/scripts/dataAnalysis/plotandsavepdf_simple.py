import labrad
import numpy
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

#change directory
dv.cd(['','QuickMeasurements', 'Power Monitoring'])
dv.open(5)
data = dv.get().asarray
voltages = data[:,1]
t = 10 * numpy.arange( voltages.size )
figure = pyplot.figure()
figure.clf()
pyplot.plot(t, voltages)
figure.suptitle('QuickMeasurements, Power Monitoring 3')
pyplot.xlabel('Time (sec)')
pyplot.ylabel('Voltages, mV')
pyplot.show()
