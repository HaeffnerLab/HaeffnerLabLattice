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
dv.cd(['','Drift_Tracking','LLI_tracking','2014Mar10'])
dv.open(3)
data = dv.get().asarray
time = data[:,0]
time = time-time[0]

interval = time[1:]-time[0:-1]

phase = data[:,1]

phase_diff = (phase[1:]-phase[0:-1])/(360*2.093)

fract_f = phase_diff/interval

m = np.size(fract_f)
#print range(0,m)
#print np.size(np.array([1,2]))

#print fract_f
deviation = []

for i in range(2,m-1):
    allan = np.sum((fract_f[1:i+2]-fract_f[0:i+1])**2)/(2*(i-1))
    allan = np.sqrt(allan)
    print allan
    deviation.append(allan)
    #deviation = np.sum((fract_f[1:i]-fract_f[0:i+1])**2)

#pyplot.plot(time[:-4],deviation,'o')
pyplot.semilogx(time[:-4],deviation,'o')
pyplot.show()
