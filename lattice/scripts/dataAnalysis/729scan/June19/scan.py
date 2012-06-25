import labrad
import numpy
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

#change directory
datasets = [203049,203703]
names = ["2012Jun19_{0:04d}_{1:02d}".format(x / 100, x % 100) for x in datasets]
labels = ["-3.5 dBm RF", "-1.7 dBm RF"]

figure = pyplot.figure()
for i,name in enumerate(names):
    print i
    dv.cd(['','Experiments','scan729',name])
    dv.open(2)
    data = dv.get().asarray
    x = data[:,0]
    y = data[:,1]
    label = names[i] + ' : ' + labels[i]
    pyplot.plot(x, y, label = label)

pyplot.legend()
pyplot.xlabel( 'Double Pass Frequency (MHz)')
pyplot.ylabel('Excitation Probability')
pyplot.title('Frequency Scan 729')
pyplot.show()
