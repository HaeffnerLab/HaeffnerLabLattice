import labrad
import numpy
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

'Zoom in of 5 ion mode'


figure = pyplot.figure()
figure.clf()


dv.cd(['','Experiments','Spectrum729','2014Jan23','1328_44'])
dv.open(1)
data = dv.get().asarray
x = data[:,0]
y = data[:,1]

#pyplot.plot(x, y,'o-')

dv.cd(['','Experiments','Spectrum729','2014Jan23','1330_06'])
dv.open(1)
data = dv.get().asarray
x = data[:,0]
y = data[:,1]

pyplot.plot(x, y,'o-')

dv.cd(['','Experiments','Spectrum729','2014Jan23','1331_42'])
dv.open(1)
data = dv.get().asarray
x = data[:,0]
y = data[:,1]

pyplot.plot(x, y,'o-')

dv.cd(['','Experiments','Spectrum729','2014Jan23','1336_54'])
dv.open(1)
data = dv.get().asarray
x = data[:,0]
y = data[:,1]

pyplot.plot(x, y,'o-')

#pyplot.title('Fast Rabi Flops', fontsize = 40)
#pyplot.xlabel(r'Time $\mu s$', fontsize = 32)
#pyplot.ylabel('Excitation percentage', fontsize = 32)
pyplot.axis([-31.20,-31.13,0,0.5])
#pyplot.tick_params(axis='both', which='major', labelsize=20)
pyplot.show()
