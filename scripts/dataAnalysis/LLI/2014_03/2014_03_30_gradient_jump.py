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
dv.cd(['','Drift_Tracking','LLI_tracking','2014Mar30'])
dv.open(7)
data = dv.get().asarray
time = data[:,0]
time = time-time[0]
phase = data[:,4]

#print np.size(time)
time = time[145:230]
time = time-time[0]
phase = phase[145:230]
phase1 = np.average(phase[0:np.size(time)/2])
phase2 = np.average(phase[np.size(time)/2:])
#print np.sqrt(np.sum((phase1-phase[0:np.size(time)/2])**2))
print phase1, np.std(phase[0:np.size(time)/2])
print phase2, np.std(phase[np.size(time)/2:])

pyplot.plot(time,phase,'o-')
pyplot.plot(time[0:np.size(time)/2],phase1*np.ones_like(time[0:np.size(time)/2]),linewidth=3.0)
pyplot.plot(time[np.size(time)/2:],phase2*np.ones_like(time[np.size(time)/2:]),linewidth=3.0)



pyplot.show()
