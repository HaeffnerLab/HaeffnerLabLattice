from matplotlib import pyplot
import numpy as np
from rabi_flop_fitter import rabi_flop_time_evolution
from lamb_dicke import lamb_dicke
from labrad.units import WithUnit
from scipy.interpolate import interp1d

trap_frequency = WithUnit(2.25, 'MHz')
projection_angle = 45
nbar = 3.0
time_2pi = 4.2#microseconds
fixed_duration_time = 5.0#microseconds

def displaced_thermal_example():
    eta = lamb_dicke.lamb_dicke(trap_frequency, projection_angle)
    excitations = np.array([])
    alphas = np.linspace(0, 25, 100)
    for alpha in alphas:
        te = rabi_flop_time_evolution(-1 ,eta)
        prob_excitation = te.compute_evolution_coherent(nbar = nbar, alpha = alpha, delta = 0, time_2pi = time_2pi, t = fixed_duration_time)
        excitations = np.append(excitations, prob_excitation)    
    interpolation_function = interp1d(excitations, alphas, kind = 'cubic')
    pyplot.figure()
    pyplot.plot(alphas, excitations, label = 'excitation to energy')
#     pyplot.figure()
    
#     sample_excitations = np.linspace(0.05,0.95,50)
#     pyplot.plot(sample_excitations, interpolation_function(sample_excitations))

#     pyplot.title('First order red sideband', fontsize = 24)
#     pyplot.tight_layout()
#     pyplot.legend(prop={'size':16})
#     pyplot.xlabel('Excitation Time (arb)', fontsize = 20)
#     pyplot.ylabel('Excitation', fontsize = 20)
#     pyplot.tick_params(axis='both', which='major', labelsize=14)
    pyplot.show()
    return interpolation_function
    
displaced_thermal_example()