from __future__ import division
import labrad
import numpy as np
from matplotlib import pyplot
import matplotlib
import lmfit

def allan_model(params, x):
    A = params['A'].value
    B = params['B'].value
    output = A/np.power(x,B)
    #output = A/(x**B)
    return output
'''
define how to compare data to the function
'''
def allan_fit(params , x, data, err):
    model = allan_model(params, x)
    return (model - data)/err


time = np.load('2014_04_18_weekend_time.npy')
time = time-time[0]

freq = np.load('2014_04_18_weekend_freq.npy')
freq_uncorrected = np.load('2014_04_18_weekend_freq_no_phase_correction.npy')
#phase = freq
phase = freq_uncorrected

interval = time[1:]-time[0:-1]

#start_bin_size = max(interval)+1 # choose bin size to have at least one data point
start_bin_size = 200
smallest_bin_size = min(interval)

print "smallest bin size =", smallest_bin_size
print "Start bin size = ", start_bin_size

##### Calculate allan deviation ####
bin_array = []
true_variance = []
avar = []
allan_error_bar = []
 
for bin_size in np.logspace(np.log10(200.0),np.log10(30000.0),num=20):
    phase_diff = []
    #print "bin_size = ", bin_size
    cf = bin_size/smallest_bin_size/19.0+1
    #cf = 1
    print "Averaging factor = ", cf
    for j in range(0,int(cf)):
        time_offset = bin_size*j/(cf)
        for i in range(0,int(np.floor(max(time-time_offset)/bin_size))-1):
            time1 = time_offset+bin_size*i
            time2 = time1+bin_size
            time3 = time2+bin_size
            where1 = np.where((time1<=time)&(time<time2))
            where2 = np.where((time2<=time)&(time<time3))
            ## skip if there is no data point in the time slice
            if not np.size(phase[where1])*np.size(phase[where2]):
                continue
            mean_phase1 = np.average(phase[where1])
            mean_phase2 = np.average(phase[where2])
            mean_phase_diff = (mean_phase2-mean_phase1)**2/2.0 ### calculate phase difference squared
            phase_diff.append(mean_phase_diff)
 
    bin_array.append(bin_size)
    avar_result = np.sqrt(np.average(phase_diff))
    avar.append(avar_result)
    M = np.size(phase_diff)
    allan_error_bar.append(avar_result*np.sqrt(0.5/(M)))
    
x = bin_array
y = avar
yerr = allan_error_bar

params = lmfit.Parameters()

params.add('A', value = 5.96)
params.add('B', value = 0.5, vary = False)

result = lmfit.minimize(allan_fit, params, args = (x, y, yerr))

fit_values  = y + result.residual

lmfit.report_errors(params)

print result.redchi
    
#pyplot.plot(bin_array,avar,'o')
#pyplot.errorbar(bin_array,avar,allan_error_bar*np.sqrt(result.redchi),fmt='o')
pyplot.errorbar(bin_array,avar,allan_error_bar,fmt='o')


##############################################

x_plot = np.linspace(np.min(x),np.max(x),1000)
#pyplot.plot(x_plot,allan_model(params,x_plot),linewidth = 1.0, linestyle = '--')



##############################################
time = np.load('2014_04_18_weekend_time.npy')
time = time-time[0]

freq = np.load('2014_04_18_weekend_freq.npy')
freq_uncorrected = np.load('2014_04_18_weekend_freq_no_phase_correction.npy')
phase = freq
#phase = freq_uncorrected

interval = time[1:]-time[0:-1]

#start_bin_size = max(interval)+1 # choose bin size to have at least one data point
start_bin_size = 200
smallest_bin_size = min(interval)

print "smallest bin size =", smallest_bin_size
print "Start bin size = ", start_bin_size

##### Calculate allan deviation ####
bin_array = []
true_variance = []
avar = []
allan_error_bar = []
 
for bin_size in np.logspace(np.log10(200.0),np.log10(30000.0),num=20):
    phase_diff = []
    #print "bin_size = ", bin_size
    cf = bin_size/smallest_bin_size/19.0+1
    #cf = 1
    print "Averaging factor = ", cf
    for j in range(0,int(cf)):
        time_offset = bin_size*j/(cf)
        for i in range(0,int(np.floor(max(time-time_offset)/bin_size))-1):
            time1 = time_offset+bin_size*i
            time2 = time1+bin_size
            time3 = time2+bin_size
            where1 = np.where((time1<=time)&(time<time2))
            where2 = np.where((time2<=time)&(time<time3))
            ## skip if there is no data point in the time slice
            if not np.size(phase[where1])*np.size(phase[where2]):
                continue
            mean_phase1 = np.average(phase[where1])
            mean_phase2 = np.average(phase[where2])
            mean_phase_diff = (mean_phase2-mean_phase1)**2/2.0 ### calculate phase difference squared
            phase_diff.append(mean_phase_diff)
 
    bin_array.append(bin_size)
    avar_result = np.sqrt(np.average(phase_diff))
    avar.append(avar_result)
    M = np.size(phase_diff)
    allan_error_bar.append(avar_result*np.sqrt(0.5/(M)))
    
x = bin_array
y = avar
yerr = allan_error_bar

params = lmfit.Parameters()

params.add('A', value = 5.96)
params.add('B', value = 0.5, vary = False)

result = lmfit.minimize(allan_fit, params, args = (x, y, yerr))

fit_values  = y + result.residual

lmfit.report_errors(params)

print result.redchi
    
#pyplot.plot(bin_array,avar,'o')
#pyplot.errorbar(bin_array,avar,allan_error_bar*np.sqrt(result.redchi),fmt='o')
pyplot.errorbar(bin_array,avar,allan_error_bar,fmt='o')


##############################################

x_plot = np.linspace(np.min(x),np.max(x),1000)
pyplot.plot(x_plot,allan_model(params,x_plot),linewidth = 1.0, linestyle = '--')
#############################################

quantum_projection = 2.28/np.sqrt(x_plot)
pyplot.plot(x_plot,quantum_projection,linewidth = 1.0,linestyle = '--')
  
pyplot.xscale('log')
pyplot.yscale('log',basey = 10,subsy=[2, 3, 4, 5, 6, 7, 8, 9])
    
ytick = [0.01,0.02,0.03,0.05,0.1,0.2]
pyplot.yticks(ytick,ytick)
xtick = [200,500,1000,2000,5000,10000, 20000, 50000]
pyplot.xticks(xtick,xtick)

pyplot.show()
