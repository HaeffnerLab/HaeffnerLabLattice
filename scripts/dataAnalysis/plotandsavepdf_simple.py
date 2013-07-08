import labrad
import numpy
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

dv.cd(['','Experiments','RabiFlopping','2013May24','1159_49'])
dv.open(1)
data = dv.get().asarray
x = data[:,0]
y = data[:,1]
figure = pyplot.figure()
figure.clf()
pyplot.plot(x, y,'o-')

pyplot.title('Fast Rabi Flops', fontsize = 40)
pyplot.xlabel(r'Time $\mu s$', fontsize = 32)
pyplot.ylabel('Excitation percentage', fontsize = 32)
pyplot.tick_params(axis='both', which='major', labelsize=20)
pyplot.show()
