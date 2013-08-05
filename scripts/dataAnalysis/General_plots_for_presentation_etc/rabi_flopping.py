import labrad
import numpy
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

#change directory
dv.cd(['','Experiments','RabiFlopping','2013Jul25','1244_36'])
dv.open(1)
data = dv.get().asarray
x = data[:,0]
y = data[:,1]
figure = pyplot.figure()
figure.clf()
pyplot.plot(x, y,'o-')

figure.suptitle('Rabi oscillations at high axial trap frequency')
pyplot.xlabel('Time (us)')
pyplot.ylabel('Excitation percentage')
pyplot.show()
