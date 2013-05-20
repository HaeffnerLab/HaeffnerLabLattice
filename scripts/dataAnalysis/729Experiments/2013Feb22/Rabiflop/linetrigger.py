import labrad
import numpy
import matplotlib

from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault
figure = pyplot.figure()
pyplot.title("Carrier at different trigger delay")

dv.cd(['', 'Experiments', '729Experiments', 'Spectrum', '2013Feb14', '1122_48'])
dv.open(1)
data = dv.get().asarray
x = (data[:,0]+15.7)*1000
pyplot.plot(x, data[:,1],'o-')

dv.cd(['', 'Experiments', '729Experiments', 'Spectrum', '2013Feb14', '1124_04'])
dv.open(1)
data = dv.get().asarray
x = (data[:,0]+15.7)*1000
pyplot.plot(x, data[:,1],'o-')

dv.cd(['', 'Experiments', '729Experiments', 'Spectrum', '2013Feb14', '1125_09'])
dv.open(1)
data = dv.get().asarray
x = (data[:,0]+15.7)*1000
pyplot.plot(x, data[:,1],'o-')

dv.cd(['', 'Experiments', '729Experiments', 'Spectrum', '2013Feb14', '1125_47'])
dv.open(1)
data = dv.get().asarray
x = (data[:,0]+15.7)*1000
pyplot.plot(x, data[:,1],'o-')

dv.cd(['', 'Experiments', '729Experiments', 'Spectrum', '2013Feb14', '1126_28'])
dv.open(1)
data = dv.get().asarray
x = (data[:,0]+15.7)*1000
pyplot.plot(x, data[:,1],'o-')

#figure.suptitle('QuickMeasurements, Power Monitoring 3')
#pyplot.xlabel('Time (sec)')
#pyplot.ylabel('Voltages, mV')
pyplot.ylabel('Excitation Probability')
pyplot.xlabel('Frequency (kHz)')
pyplot.ylim([0,1])
pyplot.xlim([-12,-8])
pyplot.show()
