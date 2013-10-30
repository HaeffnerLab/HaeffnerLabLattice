import lmfit
import labrad
from labrad import types as T
from rabi_flop_fitter.lamb_dicke import lamb_dicke
from rabi_flop_fitter.rabi_flop_fitter import rabi_flop_time_evolution
import numpy as np
from matplotlib import pyplot

'''
script parameters
'''
# info = ('Carrier', ('2013Oct09','1853_33')); alpha_guess = 0.0; max_range = 40; excitation_scaling = 0.95; sideband_order = 0
# info = ('Sideband', ('2013Oct09','1852_30')); alpha_guess = 0.0; max_range = 40; excitation_scaling = 0.95; sideband_order = -1
# info = ('Sideband', ('2013Oct09','1854_51')); alpha_guess = 1.0; max_range = 40; excitation_scaling = 0.5; sideband_order = -1
# info = ('Sideband', ('2013Oct09','1855_39')); alpha_guess = 5.0; max_range = 100; excitation_scaling = 0.5; sideband_order = -2
# info = ('Sideband', ('2013Oct09','1856_21')); alpha_guess = 15.0; max_range = 20; excitation_scaling = 0.5; sideband_order = -1
# info = ('Sideband', ('2013Oct09','1857_10')); alpha_guess = 15.0; max_range = 20; excitation_scaling = 0.5; sideband_order = -2
# info = ('Sideband', ('2013Oct09','1857_53')); alpha_guess = 15.0; max_range = 100; excitation_scaling = 0.5; sideband_order = -3
info = ('Sideband', ('2013Oct09','1858_49')); alpha_guess = 33.6; max_range = 200; excitation_scaling = 0.5; sideband_order = -1
# info = ('Sideband', ('2013Oct09','1859_23')); alpha_guess = 25.0; max_range = 100; excitation_scaling = 0.5; sideband_order = -2
# info = ('Sideband', ('2013Oct09','1900_02')); alpha_guess = 35.0; max_range = 100; excitation_scaling = 0.5; sideband_order = -3
# info = ('Sideband', ('2013Oct09','1900_35')); alpha_guess = 40.0; max_range = 13; excitation_scaling = 0.5; sideband_order = -1
# info = ('Sideband', ('2013Oct09','1901_10')); alpha_guess = 40.0; max_range = 20; excitation_scaling = 0.5; sideband_order = -2
# info = ('Sideband', ('2013Oct09','1902_22')); alpha_guess = 60.0; max_range = 14; excitation_scaling = 0.5; sideband_order = -1
# info = ('Sideband', ('2013Oct09','1903_01')); alpha_guess = 70.0; max_range = 10; excitation_scaling = 0.5; sideband_order = -2
# info = ('Sideband', ('2013Oct09','1903_35')); alpha_guess = 70.0; max_range = 10; excitation_scaling = 0.5; sideband_order = -3

# info = ('Sideband', ('2013Oct09','1707_14')); alpha_guess = 0.0; max_range = 100; excitation_scaling = 1.0; sideband_order = -1
# info = ('Sideband', ('2013Oct09','1707_47')); alpha_guess = 0.0; max_range = 50; excitation_scaling =  0.6; sideband_order = -1
# info = ('Sideband', ('2013Oct09','1708_26')); alpha_guess = 0.0; max_range = 100; excitation_scaling =  0.6; sideband_order = -1
#info = ('Sideband', ('2013Oct09','1709_43')); alpha_guess = 0.0; max_range = 100; excitation_scaling =  0.6; sideband_order = -1
# info = ('Sideband', ('2013Oct09','1710_21')); alpha_guess = 0.0; max_range = 100; excitation_scaling =  0.6; sideband_order = -1

trap_frequency = T.Value(3.0, 'MHz')
projection_angle = 45 #degrees
offset_time = 0.8
fitting_region = (0, max_range) #microseconds
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
params.add('excitation_scaling', value = excitation_scaling, vary = False)
params.add('detuning', value = 0, vary = False) #units T rabi frequency
params.add('time_2pi', value = 7.8 ,min = 0.0, vary = False) #microseconds
params.add('nbar', value = 3.15, min = 0.0, max = 200.0, vary = True)
params.add('alpha', value = alpha_guess, min = 0.0, max = 200.0, vary = True)
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

# 
# alpha = params['alpha'].value
# nbar = params['nbar'].value
# t2pi = params['time_2pi']
# op_eff = 0.5
# 
# y_values = op_eff * np.exp(-1./2*eta.value**2)**2 * (eta.value)**2 * (alpha**2 + nbar) * (np.pi / t2pi)**2 * (detailed_times- offset_time)**2


'''
make the plot
'''
pyplot.figure()
# pyplot.plot(detailed_times, guess_evolution, '--k', alpha = 0.5, label = 'initial guess')
pyplot.plot(times, prob, 'ob', label = 'data')
pyplot.plot(detailed_times, fit_values, 'r', label = 'fitted')
# pyplot.plot(detailed_times, y_values, 'b', label = 'simplified')

pyplot.legend()
pyplot.title(title, fontsize = 16)
pyplot.xlabel('time (us)', fontsize = 16)
pyplot.ylabel('D state occupation probability', fontsize = 16)
pyplot.annotate('detuning = {0}'.format(params['detuning'].value), (0.55,0.30), xycoords = 'figure fraction', fontsize = 16)
pyplot.annotate('nbar = {:.1f}'.format(params['nbar'].value), (0.55,0.25), xycoords = 'figure fraction', fontsize = 16)
pyplot.annotate('Carrier 2 Pi Time = {:.1f} us'.format(params['time_2pi'].value), (0.55,0.20), xycoords = 'figure fraction', fontsize = 16)
pyplot.annotate('alpha = {0:.1f}'.format(params['alpha'].value), (0.55,0.15), xycoords = 'figure fraction', fontsize = 16)
pyplot.tick_params(axis='both', which='major', labelsize=16)
pyplot.tight_layout()
pyplot.xlim([0,100])
pyplot.ylim([0,1.0])
pyplot.show()