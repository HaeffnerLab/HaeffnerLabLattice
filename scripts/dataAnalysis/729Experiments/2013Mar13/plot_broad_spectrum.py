import labrad
import numpy
import matplotlib

from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

#change directory
#dv.cd(['','QuickMeasurements', 'Power Monitoring'])
dv.cd(['','Experiments','Spectrum729','2013Mar13','1623_50'])
dv.open(1)
data = dv.get().asarray
x = data[:,0]
y = data[:,1]
figure = pyplot.figure()
figure.clf()
pyplot.plot(x, y,'o-')

figure.suptitle('Spectrum 2013Mar13 1623_50, 10ms excitation')
pyplot.xlabel('Frequency (MHz)')
pyplot.ylabel('Excitation percentage')
pyplot.show()
