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
#time = time_early
phase = np.append(phase_early,phase_late)
#phase = phase_early
#time = time[200:800]
time = time-time[0]
#phase = phase[200:800]
#phase = phase - 1.688586*np.cos(2*np.pi*time*(1/(12*3600))+0.705601)-223.267
#phase = phase - 2.661369*np.cos(2*np.pi*time*0.000049-2.618545)-0.068592

#pyplot.plot(time,phase,'o-')

ramsey_time = 0.048

phase = phase/360.0/ramsey_time ## convert phase to frequency sensitivity

interval = time[1:]-time[0:-1]

start_bin_size = max(interval)+1 # choose bin size to have at least one data point
smallest_bin_size = min(interval)


print start_bin_size
 
#print max(interval)
 
##### Calculate allan deviation ####
bin_array = []
true_variance = []
avar = []
allan_error_bar = []
print start_bin_size/smallest_bin_size
#cf = 4
cf = int(start_bin_size/smallest_bin_size)
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
    
pyplot.plot(bin_array,avar,'o')
pyplot.errorbar(bin_array,avar,allan_error_bar)
  
pyplot.xscale('log')
pyplot.yscale('log',basey = 10,subsy=[2, 3, 4, 5, 6, 7, 8, 9])
   
ytick = [0.003,0.01,0.02,0.03,0.05,0.1,0.2,0.3]
pyplot.yticks(ytick,ytick)
xtick = [20,50,100,200,500,1000,2000,5000,10000, 20000]
pyplot.xticks(xtick,xtick)

pyplot.show()
