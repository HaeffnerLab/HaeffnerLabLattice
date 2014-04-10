import labrad
import numpy as np
from matplotlib import pyplot
import lmfit


cxn = labrad.connect()
dv = cxn.data_vault

#change directory

figure = pyplot.figure(1)
figure.clf()


#dv.cd(['','Experiments','Ramsey2ions_ScanGapParity','2014Jan29','1756_34'])
dv.cd(['','Drift_Tracking','LLI_tracking','2014Mar16'])
dv.open(3)
data = dv.get().asarray
time = data[:,0]

phase = data[:,1]

time = time[122:245]
time = time-time[0]
phase = phase[122:245]

#for i in range(2,m-1):
#    allan = np.sum((fract_f[1:i+2]-fract_f[0:i+1])**2)/(2*(i-1))
#    allan = np.sqrt(allan)
#    print allan
#    deviation.append(allan)
    #deviation = np.sum((fract_f[1:i]-fract_f[0:i+1])**2)

#pyplot.plot(time[:-4],deviation,'o')
pyplot.plot(time,phase,'o-')
pyplot.show()
