from __future__ import division
import labrad
import numpy as np
from matplotlib import pyplot
import matplotlib
import lmfit


cxn = labrad.connect()
dv = cxn.data_vault

#change directory

figure = pyplot.figure(1)
figure.clf()


#dv.cd(['','Experiments','Ramsey2ions_ScanGapParity','2014Jan29','1756_34'])
dv.cd(['','Experiments','Rabi_power_flopping_2ions','2014Mar16','1211_26'])
dv.open(1)
data = dv.get().asarray
power = data[:,0]
excitation = data[:,1]


pyplot.plot(power,excitation,'o-')

    
#pyplot.plot(bin_array,avar,'o')
#pyplot.errorbar(bin_array,avar,allan_error_bar)

#pyplot.xscale('log')
# #pyplot.yscale('log',basey = 10,subsy=[2, 3, 4, 5, 6, 7, 8, 9])
#pyplot.yscale('log',basey = 10)
# 
#pyplot.yticks([0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.8,1.0],[0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.8,1.0])

#pyplot.xticks([20,50,100,200,500,1000,2000,5000],[20,50,100,200,500,1000,2000,5000])

pyplot.show()
