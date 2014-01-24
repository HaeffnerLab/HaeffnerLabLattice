import labrad
import numpy
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

#change directory

figure = pyplot.figure(1)
figure.clf()

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1413_53'])
dv.open(1)
data0 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1419_21'])
dv.open(1)
data1 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1422_58'])
dv.open(1)
data2 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1430_05'])
dv.open(1)
data3 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1433_51'])
dv.open(1)
data4 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1439_06'])
dv.open(1)
data5 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1442_53'])
dv.open(1)
data6 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1448_08'])
dv.open(1)
data7 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1451_54'])
dv.open(1)
data8 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1411_45'])
dv.open(1)
data9 = dv.get().asarray

dephase = (data0+data1+data2+data3+data4+data5+data6+data7+data8+data9)/10.0

plot1 = figure.add_subplot(211)

pyplot.plot(dephase[:,0], dephase[:,1],'o-',color='green')


dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1411_45'])
dv.open(1)
data0 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1421_09'])
dv.open(1)
data1 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1428_17'])
dv.open(1)
data2 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1431_53'])
dv.open(1)
data3 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1437_17'])
dv.open(1)
data4 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1440_54'])
dv.open(1)
data5 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1446_19'])
dv.open(1)
data6 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1449_56'])
dv.open(1)
data7 = dv.get().asarray

#dv.cd(['','Experiments','Dephase Scan Duration','2014Jan23','1434_43'])
#dv.open(1)
#data8 = dv.get().asarray


phase = (data0+data1+data2+data3+data4+data5+data6+data7)/8.0

error_phase = numpy.std([data0[:,1],data1[:,1],data2[:,1],data3[:,1],data4[:,1],data5[:,1],data6[:,1],data7[:,1]],axis=0)

#pyplot.errorbar(phase[:,0], phase[:,1],error_phase)
pyplot.plot(phase[:,0], phase[:,1],'o-r')
pyplot.fill_between(phase[:,0],phase[:,1]+error_phase/2.0,phase[:,1]-error_phase/2.0,alpha=0.5,color='red')

plot2 = figure.add_subplot(212)

pyplot.plot(phase[:,0], phase[:,1]-dephase[:,1],'o-')
pyplot.axis([0,300,0.0,0.25])

#figure.suptitle('Spectrum 2013Mar13 1623_50, 10ms excitation')
#pyplot.ylabel('Excitation percentage')
pyplot.show()
