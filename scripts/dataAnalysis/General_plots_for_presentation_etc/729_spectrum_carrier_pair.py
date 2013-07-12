import labrad
import numpy
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

'Two remaining carriers after proper choice of polarization and optical pumping'

dv.cd(['','Experiments','Spectrum729','2013Jun05','1653_44'])
dv.open(1)
data = dv.get().asarray
x = data[:,0]

#shift to line center
x = x + 15.44

y = data[:,1]
figure = pyplot.figure()
figure.clf()
pyplot.plot(x, y,'o-')

#pyplot.title('Fast Rabi Flops', fontsize = 40)
#pyplot.xlabel(r'Time $\mu s$', fontsize = 32)
#pyplot.ylabel('Excitation percentage', fontsize = 32)
pyplot.axis([-5,5,0,1])
#pyplot.tick_params(axis='both', which='major', labelsize=20)
pyplot.show()
