import labrad
import numpy
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

#change directory
#dv.cd(['','QuickMeasurements', 'Power Monitoring'])
dv.cd(['','Experiments','729Experiments','RabiFlopping','2012Nov02','2112_52'])
dv.open(1)
data = dv.get().asarray
x = data[:,0]
y = data[:,1]
figure = pyplot.figure()
figure.clf()
pyplot.plot(x, y)

dv.cd(['','Experiments','729Experiments','RabiFlopping','2012Nov02','2114_38'])
dv.open(1)
data = dv.get().asarray
x = data[:,0]
y = data[:,1]

pyplot.plot(x, y)

dv.cd(['','Experiments','729Experiments','RabiFlopping','2012Nov02','2119_33'])
dv.open(1)
data = dv.get().asarray
x = data[:,0]
y = data[:,1]

pyplot.plot(x, y)

#figure.suptitle('QuickMeasurements, Power Monitoring 3')
#pyplot.xlabel('Time (sec)')
#pyplot.ylabel('Voltages, mV')
pyplot.show()
