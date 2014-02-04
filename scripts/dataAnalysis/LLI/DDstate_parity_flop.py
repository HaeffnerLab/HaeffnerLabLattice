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


#dv.cd(['','Experiments','Ramsey2ions_ScanGapParity','2014Jan29','1756_34'])
dv.cd(['','Experiments','Ramsey2ions_ScanGapParity','2014Jan31','1722_21'])
dv.open(1)
data = dv.get().asarray
x = data[:,0]
y1 = data[:,1]
y2 = data[:,2]

pyplot.axis([5000,6400,0.0,1.0])

pyplot.plot(x, y1,'o-b')
pyplot.plot(x, y2,'o-r')

pyplot.ylabel('Individual ion excitation')



plot2 = figure.add_subplot(212)
#plot parity
#dv.cd(['','Experiments','Ramsey2ions_ScanGapParity','2014Jan29','1756_34'])
dv.cd(['','Experiments','Ramsey2ions_ScanGapParity','2014Jan31','1722_21'])
dv.open(2)
data = dv.get().asarray
x = data[:,0]
y = data[:,1]

pyplot.axis([5000,6400,-0.6,0.6])

pyplot.plot(x, y,'o-g')



#figure.suptitle('Spectrum 2013Mar13 1623_50, 10ms excitation')
pyplot.ylabel('Parity signal')
pyplot.xlabel('Time (us)')
pyplot.show()
