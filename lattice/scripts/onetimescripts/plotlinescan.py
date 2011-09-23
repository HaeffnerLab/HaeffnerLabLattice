import labrad
import numpy
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

#change directory
dv.cd(['','Calibrations'])
dv.open(107)
data = dv.get().asarray
freqs = data[:,0]
counts = data[:,1]
figure = pyplot.figure()
figure.clf()
pyplot.plot(freqs, counts)
figure.suptitle('WedSep141703242011LineScan')
pyplot.xlabel('Freq To Double Pass AO(Mhz)')
pyplot.ylabel('Counts, Arb')
pyplot.show()
