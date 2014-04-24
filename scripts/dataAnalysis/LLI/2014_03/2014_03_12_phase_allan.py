from __future__ import division
import labrad
import numpy as np
from matplotlib import pyplot
import lmfit
import numkit.timeseries as tm


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
phase = data[:,1]

time = time[100:299]
time = time-time[0]
phase = phase[100:299]

ramsey_time = 0.013

phase = phase/360.0/ramsey_time ## convert phase to frequency sensitivity

interval = time[1:]-time[0:-1]

start_bin_size = max(interval)+1 # choose bin size to have at least one data point

##### Calculate allan deviation ####
bin_array = []
true_variance = []
avar = []
allan_error_bar = []
#for bin_size in np.linspace(start_bin_size,max(time)/2.0,int(max(time)/2.0/start_bin_size)):
for bin_size in np.linspace(0.0,max(time)/3.0,40):
#print range(0,int(np.floor(max(time)/bin_size)))
    if bin_size<start_bin_size:
        continue
    mean_phase_data = []
    #print int(np.floor(max(time)/bin_size))
    for i in range(0,int(np.floor(max(time)/bin_size))):
        where = np.where((bin_size*i<time)&(time<bin_size*(i+1)))
        mean_phase = np.average(phase[where])
        mean_phase_data.append(mean_phase)
    
    bin_array.append(bin_size) 
    true_variance.append(np.std(mean_phase_data))
    mean_phase_diff = np.array(mean_phase_data[1:])-np.array(mean_phase_data[0:-1])
    phase_diff = np.sqrt(np.average(mean_phase_diff**2)/2)
    avar.append(phase_diff)
    allan_error_bar.append(phase_diff*0.5*np.sqrt(1/(i)))

#pyplot.plot(bin_array,true_variance,'o-')
pyplot.plot(bin_array,avar,'o')
pyplot.errorbar(bin_array,avar,allan_error_bar)

pyplot.xscale('log')
pyplot.yscale('log')
pyplot.show()
