import labrad
import numpy
import pylab
cxn = labrad.connect()

dv = cxn.data_vault
dv.cd('','CavityScans')
dnum = '00243'
dtex = ' - Cavity Scan 866'
fileno = dnum + dtex
dv.open(fileno) # '00243 - Cavity Scan 866'
data = dv.get()
data = numpy.transpose(data)
x = data[0];
y = data[1];

pylab.plot(x,y,'-o')
pylab.xlabel('Cavity(mV)')
pylab.ylabel('Counts(kC/s)')
#pylab.savefig(fileno)
pylab.show()