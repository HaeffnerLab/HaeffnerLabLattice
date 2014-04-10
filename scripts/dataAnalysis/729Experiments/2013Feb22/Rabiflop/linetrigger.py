import labrad
import numpy
import matplotlib

from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

center = 15.712

figure = pyplot.figure()
# pyplot.title("Carrier at different trigger delay")
dv.cd(['', 'Experiments', '729Experiments', 'Spectrum', '2013Feb14', '1122_48'])
dv.open(1)


# 0 delay 1122_48
# 7.5 ms 1124_04
# 15 ms 1125_09
# 3.75 ms 1125_47
# 10 ms 1126_28



data = dv.get().asarray
x = (data[:,0]+center)*1000
pyplot.plot(x, data[:,1],'o-', label = '0.0 ms')

# dv.cd(['', 'Experiments', '729Experiments', 'Spectrum', '2013Feb14', '1125_47'])
# dv.open(1)
# data = dv.get().asarray
# x = (data[:,0]+center)*1000
# pyplot.plot(x, data[:,1],'o-', label = '3.75 ms')

dv.cd(['', 'Experiments', '729Experiments', 'Spectrum', '2013Feb14', '1124_04'])
dv.open(1)
data = dv.get().asarray
x = (data[:,0]+center)*1000
pyplot.plot(x, data[:,1],'o-', label = '7.5 ms')

# dv.cd(['', 'Experiments', '729Experiments', 'Spectrum', '2013Feb14', '1126_28'])
# dv.open(1)
# data = dv.get().asarray
# x = (data[:,0]+center)*1000
# pyplot.plot(x, data[:,1],'o-', label = '10 ms')
# 
# dv.cd(['', 'Experiments', '729Experiments', 'Spectrum', '2013Feb14', '1125_09'])
# dv.open(1)
# data = dv.get().asarray
# x = (data[:,0]+center)*1000
# pyplot.plot(x, data[:,1],'o-', label = '15 ms')




#figure.suptitle('QuickMeasurements, Power Monitoring 3')
#pyplot.xlabel('Time (sec)')
#pyplot.ylabel('Voltages, mV')
# pyplot.ylabel('Excitation Probability')
# pyplot.xlabel('Frequency (kHz)')
pyplot.ylim([0,1])
pyplot.xlim([0,4])
pyplot.legend(prop={'size':16})
pyplot.tick_params(axis='both', which='major', labelsize=16)
figure.savefig('carrier_delay.pdf', dpi = 600)
pyplot.show()
