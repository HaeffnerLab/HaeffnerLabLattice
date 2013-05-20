import labrad
import numpy
import matplotlib

from matplotlib import pyplot
#get access to servers
cxn = labrad.connect('192.168.169.197', password = 'lab')
dv = cxn.data_vault
figure = pyplot.figure()
pyplot.title("Phase evolution due to blue detuned laser")

for dataset,comment in [('2300_48', '755.24190 (+20GHz) -3dBm'), ('2301_48', '755.24190 (+20GHz) -12dBm'), ('2303_40', '755.24190 (+20GHz) -18dBm 25 \muW'), ('2320_02', '755.48098 (+200GHz), -5dBm 200 \muW')]:
    dv.cd(['', 'Experiments', '729Experiments', 'RamseyDephase', '2013Jan25', dataset])
    dv.open(1)
    data = dv.get().asarray
    x = data[:,0] * 10**6
    pyplot.plot(x, data[:,1],'o-', label = '2013Jan26_{0} {1}'.format(dataset, comment))

pyplot.ylabel('Excitation Probability')
pyplot.xlabel(r'Blue Pulse Duration $\mu s$')
pyplot.ylim([0,1])
pyplot.legend()
pyplot.show()
