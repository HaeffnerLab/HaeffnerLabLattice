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

result_slope = []
for i in range(0,30):
    ####simulation###
    time = np.linspace(0,80000.0,80000.0/61)
    phase = np.random.normal(0,0.350,np.size(time))
    ####
    interval = time[1:]-time[0:-1]
    
    #start_bin_size = max(interval)+1 # choose bin size to have at least one data point
    start_bin_size = 200
    #smallest_bin_size = min(interval)
    
    
    #print "Start bin size = ", start_bin_size
    
    ##### Calculate allan deviation ####
    bin_array = []
    true_variance = []
    avar = []
    allan_error_bar = []
    #cf = int(start_bin_size/smallest_bin_size)
    cf = 5
    #print "Averaging factor = ", cf
     
    for bin_size in np.logspace(0.0,np.log10(20000),num=34):
        if bin_size<start_bin_size:
            continue
        if bin_size>30000:
            continue
        phase_diff = []
        #print "bin_size = ", bin_size
        #cf = int(bin_size/smallest_bin_size/10.0)+1
        #cf = 1
        #print "Averaging factor = ", cf
        for j in range(0,cf):
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
    
    #lmfit.report_errors(params)
    
    slope = params['A'].value
    result_slope.append(slope)
    print "Slope = ", slope

print "Mean = ", np.average(result_slope)
