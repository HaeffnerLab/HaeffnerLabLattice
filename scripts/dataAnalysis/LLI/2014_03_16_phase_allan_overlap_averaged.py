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
dv.cd(['','Drift_Tracking','LLI_tracking','2014Mar16'])
dv.open(7)
data = dv.get().asarray
time = data[:,0]
time = time-time[0]
phase = data[:,3]

time = time[200:400]
time = time-time[0]
phase = phase[200:400]

pyplot.plot(time,phase,'o-')

ramsey_time = 0.050

phase = phase/360.0/ramsey_time ## convert phase to frequency sensitivity

interval = time[1:]-time[0:-1]

start_bin_size = max(interval)+1 # choose bin size to have at least one data point


print start_bin_size

#print max(interval)

##### Calculate allan deviation ####
bin_array = []
true_variance = []
avar = []
allan_error_bar = []
cf = 8
#print 'overlapping factor = ',cf

#print np.logspace(0.0,np.log10(max(time)/3.0),num=20, base = 10.0)

for bin_size in np.logspace(0.0,np.log10(max(time)/3.0),num=30):
    if bin_size<start_bin_size:
        continue
    phase_diff = []
    for j in range(0,cf):
        time_offset = bin_size*j/(cf)
        for i in range(0,int(np.floor(max(time-time_offset)/bin_size))-1):
            time1 = time_offset+bin_size*i
            time2 = time1+bin_size
            time3 = time2+bin_size
            where1 = np.where((time1<=time)&(time<time2))
            where2 = np.where((time2<=time)&(time<time3))
            mean_phase1 = np.average(phase[where1])
            mean_phase2 = np.average(phase[where2])
            mean_phase_diff = (mean_phase2-mean_phase1)**2/2.0 ### calculate phase difference squared
            phase_diff.append(mean_phase_diff)

    bin_array.append(bin_size)
    avar_result = np.sqrt(np.average(phase_diff))
    avar.append(avar_result)
    M = np.size(phase_diff)
    allan_error_bar.append(avar_result*np.sqrt(0.5/(M)))
    
#pyplot.plot(bin_array,avar,'o')
#pyplot.errorbar(bin_array,avar,allan_error_bar)

#pyplot.xscale('log')
# #pyplot.yscale('log',basey = 10,subsy=[2, 3, 4, 5, 6, 7, 8, 9])
#pyplot.yscale('log',basey = 10)
# 
#pyplot.yticks([0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.8,1.0],[0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.8,1.0])

#pyplot.xticks([20,50,100,200,500,1000,2000,5000],[20,50,100,200,500,1000,2000,5000])

pyplot.show()
