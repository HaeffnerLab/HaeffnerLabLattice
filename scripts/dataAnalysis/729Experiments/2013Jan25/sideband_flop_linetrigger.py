import labrad
import numpy
import matplotlib

from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault
figure = pyplot.figure()
pyplot.title("Sideband Rabi Flopping")

dv.cd(['', 'Experiments', '729Experiments', 'RabiFlopping', '2013Jan25', '1707_40'])
dv.open(1)
data = dv.get().asarray
x = data[:,0] * 10**6 #now in microseconds
pyplot.plot(x, data[:,1],'o-', label = '2013Jan251707_40 no linetrigger')

dv.cd(['', 'Experiments', '729Experiments', 'RabiFlopping', '2013Jan25', '1705_00'])
dv.open(1)
data = dv.get().asarray
x = data[:,0] * 10**6 #now in microseconds
pyplot.plot(x, data[:,1],'o-', label = '2013Jan251705_00 yes linetrigger')

#figure.suptitle('QuickMeasurements, Power Monitoring 3')
#pyplot.xlabel('Time (sec)')
#pyplot.ylabel('Voltages, mV')
pyplot.ylabel('Excitation Probability')
pyplot.xlabel(r'Excitation Time $\mu s$')
pyplot.ylim([0,1])
pyplot.legend()
pyplot.show()
