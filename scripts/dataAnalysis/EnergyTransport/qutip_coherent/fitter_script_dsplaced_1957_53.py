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
info = ('Carrier Flops', ('2013Aug26','1957_53'))
trap_frequency = T.Value(3.0, 'MHz')
projection_angle = 45 #degrees
offset_time = 0.8
sideband_order = 1
fitting_region = (0, 40) #microseconds
'''
compute lamb dicke parameter
'''
eta = lamb_dicke.lamb_dicke(trap_frequency, projection_angle)
print 'Lamb Dicke parameter: {0:.2f}'.format(eta)
'''
initialize the fitter
'''
flop = rabi_flop_time_evolution(sideband_order, eta)
'''
create fitting parameters
'''
params = lmfit.Parameters()
params.add('excitation_scaling', value = 0.5, vary = False)
params.add('detuning', value = 0, vary = 0) #units of rabi frequency
params.add('time_2pi', value = 7.6, vary = 0) #microseconds
params.add('nbar', value = 0.61, min = 0.0, max = 200.0, vary = 0)
params.add('alpha', value = 14.0, min = 0.0, max = 200.0, vary = 1)
'''
load the dataset
'''
dv = labrad.connect().data_vault
title,dataset = info 
date,datasetName = dataset
dv.cd( ['','Experiments','Blue Heat RabiFlopping',date,datasetName] )
dv.open(1)  
times,prob = dv.get().asarray.transpose()
tmin,tmax = times.min(), times.max()
detailed_times = np.linspace(tmin, tmax, 1000)
'''
compute time evolution of the guessed parameters
'''
guess_evolution = flop.compute_evolution_coherent(params['nbar'].value , params['alpha'].value, params['detuning'].value, params['time_2pi'].value, detailed_times - offset_time, excitation_scaling = params['excitation_scaling'].value)

'''
define how to compare data to the function
'''
def rabi_flop_fit_thermal(params , t, data):
    model = flop.compute_evolution_coherent(params['nbar'].value , params['alpha'].value, params['detuning'].value, params['time_2pi'].value, t - offset_time, excitation_scaling = params['excitation_scaling'].value)
    return model - data
'''
perform the fit
'''
region = (fitting_region[0] <= times) * (times <= fitting_region[1])
result = lmfit.minimize(rabi_flop_fit_thermal, params, args = (times[region], prob[region]))
fit_values = flop.compute_evolution_coherent(params['nbar'].value , params['alpha'].value, params['detuning'].value, params['time_2pi'].value, detailed_times - offset_time, excitation_scaling = params['excitation_scaling'].value)
lmfit.report_errors(params)
'''
make the plot
'''
pyplot.figure()
pyplot.plot(detailed_times, guess_evolution, '--k', alpha = 0.5, label = 'initial guess')
pyplot.plot(times, prob, 'ob', label = 'data')
pyplot.plot(detailed_times, fit_values, 'r', label = 'fitted')
pyplot.legend()
pyplot.title(title)
pyplot.xlabel('time (us)')
pyplot.ylabel('D state occupation probability')
pyplot.text(max(times)*0.70,0.68, 'detuning = {0}'.format(params['detuning'].value))
pyplot.text(max(times)*0.70,0.73, 'nbar = {:.0f}'.format(params['nbar'].value))
pyplot.text(max(times)*0.70,0.78, '2 Pi Time = {:.1f} us'.format(params['time_2pi'].value))
pyplot.show()