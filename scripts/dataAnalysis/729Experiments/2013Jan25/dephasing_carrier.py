import labrad
import numpy
import matplotlib

from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault
figure = pyplot.figure()
pyplot.title("Rabi Flop on Carrier with AC Stark phase evolution")

for date,dataset,comment in [('2013Jan25', '2359_04', 'no dephasing'), ('2013Jan25', '2359_41','additional pi phase shift'), ('2013Jan26', '0000_17','additional 2pi phase shift')]:
    dv.cd(['', 'Experiments', '729Experiments', 'RamseyDephase', date, dataset])
    dv.open(1)
    data = dv.get().asarray
    x = data[:,0] * 10**6
    pyplot.plot(x, data[:,1],'o-', label = '2013Jan26_{0} {1}'.format(dataset, comment))

pyplot.ylabel('Excitation Probability')
pyplot.xlabel(r'729 Excitation Time $\mu s$')
pyplot.ylim([0,1])
pyplot.legend()
pyplot.show()
