import numpy as np
from matplotlib import pyplot
import lmfit

#ion / frequency in Hz
length_scale = 13.0 #microns for 200 kHz
ions = np.array([1, 2, 3, 4])
ion_positions = length_scale * ions
#shift positions such that center is at 0
ion_positions = ion_positions - np.average(ions) * length_scale

rabi_frequency = np.array([33367, 51432, 13791, 0])


params = lmfit.Parameters()
params.add('amplitude', value = rabi_frequency.max())
params.add('center', value = 1.5)
params.add('beam_waist', value = length_scale)

'''
define the function
'''
def intensity_profile(params, x):
    ###gaussian profile for intensity of the laser beam
    amplitude = params['amplitude'].value
    center = params['center'].value
    beam_waist = params['beam_waist'].value
    model =  amplitude * np.exp( - 2 * (x - center)**2 / (beam_waist**2))
    return model
'''
define how to compare data to the function
'''
def intensity_fit(params , x, data):
    model = intensity_profile(params, x)
    return model - data

result = lmfit.minimize(intensity_fit, params, args = (ion_positions, rabi_frequency))
pyplot.plot(ion_positions, rabi_frequency / 10**3, '*')

sample = np.linspace(ion_positions.min(), ion_positions.max(), 100)
fit_profile = intensity_profile(params, sample)
pyplot.plot(sample, fit_profile / 10**3, label = 'beam waist {0:.0f} microns'.format(params['beam_waist'].value))

lmfit.report_errors(params)
pyplot.xlim([-30,30])
pyplot.xlabel('microns', fontsize = 30)
pyplot.ylabel('Rabi Frequency [kHz]', fontsize = 30)
pyplot.tick_params(axis='both', which='major', labelsize=25)
pyplot.legend(prop={'size':30})
pyplot.show()