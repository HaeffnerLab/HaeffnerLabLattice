from __future__ import division
import labrad
import numpy as np
from matplotlib import pyplot
import matplotlib
import lmfit
import processFFT


def cosine_model(params, x):
    A = params['A'].value
    freq = params['freq'].value
    phase=params['phase'].value
    offset=params['offset'].value
    output = A*np.cos(2*np.pi*x*freq+phase)+offset
    return output
'''
define how to compare data to the function
'''
def cosine_fit(params , x, data, err):
    model = cosine_model(params, x)
    return (model - data)/err



cxn = labrad.connect()
dv = cxn.data_vault

#change directory

figure = pyplot.figure(1)
figure.clf()


#dv.cd(['','Experiments','Ramsey2ions_ScanGapParity','2014Jan29','1756_34'])
dv.cd(['','Drift_Tracking','LLI_tracking_2_points','2014Apr09'])
dv.open(1)
data = dv.get().asarray
time = data[:,0]
#time = time-time[0]
phase = data[:,9]

time = time[10:]
phase = phase[10:]


where_early = np.where(time>50000)
where_late = np.where(time<50000)

time_early = time[where_early]
phase_early = phase[where_early]
time_late = time[where_late]
phase_late = phase[where_late]
time_late = time_late+86400 ###went over night

time = np.append(time_early,time_late)
phase = np.append(phase_early,phase_late)
#time = time[200:800]
time = time-time[0]
#phase = phase[200:800]
#phase = phase - 1.688586*np.cos(2*np.pi*time*(1/(12*3600))+0.705601)-223.267
#phase = phase - 2.661369*np.cos(2*np.pi*time*0.000049-2.618545)-0.068592
print phase
freqs = processFFT.computeFreqDomain(phase, 1.0,  1.0, 1.0)
