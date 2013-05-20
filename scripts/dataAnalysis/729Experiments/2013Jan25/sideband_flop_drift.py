import labrad
import numpy
import matplotlib

from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault
figure = pyplot.figure()
pyplot.title("Sideband Rabi Flopping Drift, all same parameters")

for dataset in ['2217_20','2211_05', '2219_42','2218_33']:
    dv.cd(['', 'Experiments', '729Experiments', 'RabiFlopping', '2013Jan25', dataset])
    dv.open(1)
    data = dv.get().asarray
    x = data[:,0] * 10**6 #now in microseconds
    pyplot.plot(x, data[:,1],'o-', label = '2013Jan25_{0}'.format(dataset))

pyplot.ylabel('Excitation Probability')
pyplot.xlabel(r'Excitation Time $\mu s$')
pyplot.ylim([0,1])
pyplot.legend()
pyplot.show()
