import lmfit
import labrad
from labrad import types as T
from lamb_dicke import lamb_dicke
from rabi_flop_fitter import rabi_flop_time_evolution
import numpy as np
from matplotlib import pyplot

'''
script parameters
'''
#5 ions
# info = ('Carrier Flops', ('2013Nov20','1544_37')); sideband_order = -1#13.727020 +/- 0.825951 (6.02%) 
# info = ('Carrier Flops', ('2013Nov20','1534_54')); sideband_order = 0 #2pitime 7.87mus, left ion
# info = ('Carrier Flops', ('2013Nov20','1612_55')); sideband_order = 0 #2pitime 7.4mus, center ion
# info = ('Carrier Flops', ('2013Nov20','1641_20')); sideband_order = 0 #2pitime 7.9mus, right ion
#15 ions
# info = ('Carrier Flops', ('2013Nov20','1720_27')); sideband_order = 0 #2pitime 7.91mus, left ion
# info = ('Carrier Flops', ('2013Nov20','1726_27')); sideband_order = -1#9.345554 +/- 0.882314
# info = ('Carrier Flops', ('2013Nov20','1917_49')); sideband_order = 0 #2pitime 6.3mus, right ion
#25 ions
# info = ('Carrier Flops', ('2013Nov20','1949_33')); sideband_order = 0 #2pitime 7.6mus, left ion
# info = ('Sideband Flops', ('2013Nov20','2000_41')); sideband_order = -1#5.505775 +/- 0.666371, excitation at 7.5: 0.09490763
# info = ('Carrier Flops', ('2013Nov20','2132_23')); sideband_order = 0 #2pitime 7.6mus, left ion

trap_frequency = T.Value(2.25, 'MHz')
projection_angle = 45 #degrees
offset_time = 0.2
fitting_region = (0,7) #microseconds
'''
compute lamb dicke parameter
'''
eta = lamb_dicke.lamb_dicke(trap_frequency, projection_angle)
print 'Lamb Dicke parameter: {0:.3f}'.format(eta)
'''
initialize the fitter
'''
flop = rabi_flop_time_evolution(sideband_order, eta)
'''
create fitting parameters
'''
params = lmfit.Parameters()
params.add('excitation_scaling', value = 1.0, vary = False)
params.add('detuning', value = 0, vary = False) #units of rabi frequency
params.add('time_2pi', value = 8.0, vary = True, min = 0.0) #microseconds
params.add('nbar', value = 10., min = 0.0, max = 200.0, vary = False)
'''
load the dataset
'''
dv = labrad.connect().data_vault
title,dataset = info 
date,datasetName = dataset
dv.cd( ['','Experiments','RabiFlopping',date,datasetName] )
dv.open(1)
data = dv.get().asarray.transpose()
times,prob = data[0],data[1]
# times,prob = data[0],data[2]
tmin,tmax = times.min(), times.max()
detailed_times = np.linspace(tmin, tmax, 1001)
'''
compute time evolution of the guessed parameters
'''
guess_evolution = flop.compute_evolution_thermal(params['nbar'].value , params['detuning'].value, params['time_2pi'].value, detailed_times - offset_time, excitation_scaling = params['excitation_scaling'].value)

'''
define how to compare data to the function
'''
def rabi_flop_fit_thermal(params , t, data):
    model = flop.compute_evolution_thermal(params['nbar'].value, params['detuning'].value, params['time_2pi'].value, t, excitation_scaling = params['excitation_scaling'].value)
#     error = np.sqrt(data) * np.sqrt(1 - data) / np.sqrt(readouts)
    return (model - data)# / error
'''
perform the fit
'''
region = (fitting_region[0] <= times) * (times <= fitting_region[1])
result = lmfit.minimize(rabi_flop_fit_thermal, params, args = (times[region], prob[region]))
fit_values = flop.compute_evolution_thermal(params['nbar'].value , params['detuning'].value, params['time_2pi'].value, detailed_times - offset_time, excitation_scaling = params['excitation_scaling'].value )
lmfit.report_errors(params)
'''
make the plot
'''
pyplot.figure()
pyplot.plot(detailed_times, guess_evolution, '--k', alpha = 0.5, label = 'initial guess')
print 'excitation at 7.5 mus', fit_values[(detailed_times <= 7.6) * (detailed_times >= 7.4)]
pyplot.plot(times, prob, 'ob', label = 'data')
pyplot.plot(detailed_times, fit_values, 'r', label = 'fitted')
# pyplot.legend()
pyplot.title(title)
pyplot.xlabel('time (us)')
pyplot.ylabel('D state occupation probability')
pyplot.text(max(times)*0.70,0.68, 'detuning = {0}'.format(params['detuning'].value))
pyplot.text(max(times)*0.70,0.73, 'nbar = {:.0f}'.format(params['nbar'].value))
pyplot.text(max(times)*0.70,0.78, '2 Pi Time = {:.1f} us'.format(params['time_2pi'].value))
pyplot.show()