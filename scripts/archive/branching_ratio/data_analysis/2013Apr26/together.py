from __future__ import division
import numpy as np
import matplotlib
#from constants import constants as c

from matplotlib import pyplot
import lmfit

#in the form angle  branching fraction , error
data = [
        [np.arctan((25.0-325.0)/ 1000.0), 0.93565,   16*10**-5],
        [np.arctan((175.0-325.0)/ 1000.0), 0.93543,  13*10**-5],
        [np.arctan((325.0-325.0)/ 1000.0), 0.93551,  13*10**-5],
        [np.arctan((575.0-325.0)/ 1000.0), 0.93574,  17*10**-5],
        [np.arctan((575.0-325.0)/ 1000.0), 0.93574,  17*10**-5],
        [np.pi*90.0 / 180.0, 0.93597,  11*10**-5],
        [np.pi*-90.0 / 180.0, 0.93595,  13*10**-5],
        [np.arctan((325.0-325.0)/ 1000.0), 0.93536,  17*10**-5],
        ]
data = np.array(data)
pyplot.figure()
#finding the angle 325mA corresponds to angle of 0, and then we apply 1000ma to the other axis
pyplot.errorbar(180.0 / np.pi * data[:,0], y = data[:,1], yerr = data[:,2], fmt = '*')
pyplot.errorbar(0, y = 0.93565, yerr = 5e-5, fmt = '*r')
pyplot.xlabel('B field direction (deg)')
pyplot.ylabel('Branching Fraction')


def sin_model(params, x):
    period = params['period'].value
    amplitude = params['amplitude'].value
    phase = params['phase'].value
    offset = params['offset'].value
    model =  offset + amplitude * np.sin( (x - phase) / (period / (2*np.pi)))
    return model

def sin_fit(params , x, data):
    model = sin_model(params, x)
    return model - data

params = lmfit.Parameters()
params.add('period', value = 2*np.pi, vary = False)
params.add('phase', value = np.pi / 4, vary = False)
params.add('amplitude', value = 10e-3)
params.add('offset', value = 0.93565)

result = lmfit.minimize(sin_fit, params, args = (data[:,0], data[:,1]), **{'ftol':1e-30, 'xtol':1e-30} )
final  = data[:,1] + result.residual
lmfit.report_errors(params)

sample = np.linspace(-np.pi, np.pi, 100)
fitted = sin_model(params, sample)
pyplot.plot(180.0 / np.pi *sample, fitted)
pyplot.xlim(-180.0,180.0)
pyplot.annotate('Amplitude {0:.2e}; Error {1:.2e}'.format(params['amplitude'].value, params['amplitude'].stderr), xy=(0.55, 0.90), xycoords='axes fraction')
pyplot.show()