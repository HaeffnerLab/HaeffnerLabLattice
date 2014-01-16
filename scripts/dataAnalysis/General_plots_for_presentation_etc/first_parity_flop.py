import labrad
import numpy
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

#change directory

figure = pyplot.figure(1)
figure.clf()
plot1 = figure.add_subplot(211)


dv.cd(['','Experiments','RamseyScanGapParity','2013Dec16','1400_50'])
dv.open(1)
data = dv.get().asarray
x = data[:,0]
y1 = data[:,1]
y2 = data[:,2]

pyplot.plot(x, y1,'o-b')
pyplot.plot(x, y2,'o-r')

dv.cd(['','Experiments','RamseyScanGapParity','2013Dec16','1403_36'])
dv.open(1)
data = dv.get().asarray
x = data[:,0]
y1 = data[:,1]
y2 = data[:,2]

pyplot.plot(x, y1,'o-b')
pyplot.plot(x, y2,'o-r')

dv.cd(['','Experiments','RamseyScanGapParity','2013Dec16','1407_16'])
dv.open(1)
data = dv.get().asarray
x = data[:,0]
y1 = data[:,1]
y2 = data[:,2]

pyplot.plot(x, y1,'o-b')
pyplot.plot(x, y2,'o-r')



plot2 = figure.add_subplot(212)
#plot parity
dv.cd(['','Experiments','RamseyScanGapParity','2013Dec16','1403_36'])
dv.open(2)
data = dv.get().asarray
x = data[:,0]
y = data[:,1]
pyplot.plot(x, y,'o-g')

dv.cd(['','Experiments','RamseyScanGapParity','2013Dec16','1400_50'])
dv.open(2)
data = dv.get().asarray
x = data[:,0]
y = data[:,1]
pyplot.plot(x, y,'o-g')

dv.cd(['','Experiments','RamseyScanGapParity','2013Dec16','1407_16'])
dv.open(2)
data = dv.get().asarray
x = data[:,0]
y = data[:,1]
pyplot.plot(x, y,'o-g')


#figure.suptitle('Spectrum 2013Mar13 1623_50, 10ms excitation')
#pyplot.ylabel('Excitation percentage')
pyplot.show()
