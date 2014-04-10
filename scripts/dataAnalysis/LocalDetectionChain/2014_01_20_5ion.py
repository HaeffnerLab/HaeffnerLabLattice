import labrad
import numpy
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

#change directory
figure = pyplot.figure(1)
figure.clf()

#36 degrees: 1340_17/1342_57
#72 degrees: 1345_26/1348_05
#108 degrees: 1350_34/1353_12
#144 degrees: 1355_40/1358_19
#180 degrees: 1400_56/1403_35
#216 degrees: 1406_11/1408_56
#254 degrees: 1411_24/1414_03
#290 degrees: 1416_31/1419_08
#326 degrees: 1434_43/1437_22

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan20','1340_17'])
dv.open(1)
data0 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan20','1342_57'])
dv.open(1)
data1 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan20','1348_05'])
dv.open(1)
data2 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan20','1353_12'])
dv.open(1)
data3 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan20','1358_19'])
dv.open(1)
data4 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan20','1403_25'])
dv.open(1)
data5 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan20','1408_56'])
dv.open(1)
data6 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan20','1414_03'])
dv.open(1)
data7 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan20','1419_08'])
dv.open(1)
data8 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan20','1437_22'])
dv.open(1)
data9 = dv.get().asarray

dephase = (data0+data1+data2+data3+data4+data5+data6+data7+data8+data9)/10.0

pyplot.plot(dephase[:,0], dephase[:,1],'o-', label = 'dephased')


dv.cd(['','Experiments','Dephase Scan Duration','2014Jan20','1340_17'])
dv.open(1)
data0 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan20','1345_26'])
dv.open(1)
data1 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan20','1350_34'])
dv.open(1)
data2 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan20','1355_40'])
dv.open(1)
data3 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan20','1400_56'])
dv.open(1)
data4 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan20','1406_11'])
dv.open(1)
data5 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan20','1411_24'])
dv.open(1)
data6 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan20','1416_31'])
dv.open(1)
data7 = dv.get().asarray

dv.cd(['','Experiments','Dephase Scan Duration','2014Jan20','1434_43'])
dv.open(1)
data8 = dv.get().asarray


phase = (data0+data1+data2+data3+data4+data5+data6+data7+data8)/9.0

pyplot.plot(phase[:,0], phase[:,1],'o-', label = 'original')

#figure.suptitle('Spectrum 2013Mar13 1623_50, 10ms excitation')
#pyplot.ylabel('Excitation percentage')
pyplot.ylim(0,1.0)
pyplot.legend()
pyplot.tick_params(axis='both', which='major', labelsize=16)
pyplot.savefig('correlation_transport.pdf', )
pyplot.show()
