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


cxn = labrad.connect()
dv = cxn.data_vault

#change directory

figure = pyplot.figure(1)
figure.clf()

#dv.cd(['','Experiments','Ramsey2ions_ScanGapParity','2014Jan29','1756_34'])
dv.cd(['','Drift_Tracking','LLI_tracking_all_data','2014Apr18'])
dv.open(1)
data = dv.get().asarray
time = data[:,0]

ramsey_time = 0.095
axial = (data[:,12]-np.average(data[:,12]))*1000*0.027*ramsey_time*360 ## convert to phase
fractional_b_field = (data[:,10]-np.average(data[:,10]))/np.average(data[:,10])
            
b_field = fractional_b_field*2*8*ramsey_time*360

#time = time-time[0]
#3 = average phase long time
#7 = average phase short time
#9 = average phase difference
dataset = 9
phase = data[:,dataset]-np.average(data[:,dataset]) #3,7,9

skip = 0

time = time[skip:]
axial = axial[skip:]
b_field = b_field[skip:]
phase = phase[skip:]

where_early = np.where(time>73500)#73000
where_late = np.where(time<32476)


time = np.append(time[where_early],time[where_late]+86400)
phase = np.append(phase[where_early],phase[where_late])
b_field = np.append(b_field[where_early],b_field[where_late])
axial = np.append(axial[where_early],axial[where_late])

b_field_correction = True
axial_correction = True
if axial_correction:
    axial[np.where(axial<-0.7)] = np.ones_like(axial[np.where(axial<-0.7)])*np.average(axial)
    phase = phase - axial
if b_field_correction:
    phase = phase - b_field

time = time-time[0]



phase = phase/360.0/ramsey_time ## convert phase to frequency sensitivity

interval = time[1:]-time[0:-1]

start_bin_size = max(interval)+1 # choose bin size to have at least one data point
#start_bin_size = 100
smallest_bin_size = min(interval)


print "Start bin size = ", start_bin_size

##### Calculate allan deviation ####
bin_array = []
true_variance = []
avar = []
allan_error_bar = []
cf = int(start_bin_size/smallest_bin_size)
#print "Averaging factor = ", cf
 
for bin_size in np.logspace(0.0,np.log10(max(time)/2.1),num=100):
    if bin_size<start_bin_size:
        continue
    phase_diff = []
    print "bin_size = ", bin_size
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
    
pyplot.plot(bin_array,avar,'o')
pyplot.errorbar(bin_array,avar,allan_error_bar)


##############################################

x_plot = np.linspace(np.min(x),np.max(x),1000)
pyplot.plot(x_plot,allan_model(params,x_plot),linewidth = 2.0)
  
pyplot.xscale('log')
pyplot.yscale('log',basey = 10,subsy=[2, 3, 4, 5, 6, 7, 8, 9])
    
ytick = [0.05,0.1,0.2,0.3]
pyplot.yticks(ytick,ytick)
xtick = [200,500,1000,2000,5000,10000, 20000]
pyplot.xticks(xtick,xtick)

pyplot.show()
