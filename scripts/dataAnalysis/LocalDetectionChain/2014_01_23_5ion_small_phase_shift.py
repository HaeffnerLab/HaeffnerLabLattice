import labrad
import numpy
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

#change directory

figure = pyplot.figure(1)
figure.clf()

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1406_44'])
dv.open(1)
data0 = dv.get().asarray

pyplot.plot(data0[:,0], data0[:,1],'o-',color='green')

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1353_33'])
dv.open(1)
data0 = dv.get().asarray

pyplot.plot(data0[:,0], data0[:,1],'o-',color='blue')


#figure.suptitle('Spectrum 2013Mar13 1623_50, 10ms excitation')
#pyplot.ylabel('Excitation percentage')
pyplot.show()
