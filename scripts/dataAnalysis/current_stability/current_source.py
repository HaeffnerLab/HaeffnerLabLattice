import labrad
import numpy as np
import matplotlib

from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

#change directory
#dv.cd(['','QuickMeasurements', 'Power Monitoring'])
dv.cd(['','QuickMeasurements','Keithly 6487 Current Monitoring','2012Aug10'])
dv.open(39)
data = dv.get().asarray
thor = data[0:76600]
ilx = data[76701:116194]
figure = pyplot.figure()
figure.clf()
pyplot.plot(ilx[:,1]-np.average(ilx[:,1]))
pyplot.plot(10*(thor[:,1]-np.average(thor[:,1])))
figure.suptitle('Current Sources')
pyplot.xlabel('Time (s)')
pyplot.ylabel('Current (A)')
pyplot.show()
