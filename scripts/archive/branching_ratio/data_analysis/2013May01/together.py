from __future__ import division
import numpy as np
import matplotlib
#from constants import constants as c

from matplotlib import pyplot
import lmfit

br = 0.93565

#in the form angle  branching fraction , error
data = np.array([
        [np.pi*-90.0 / 180.0, 0.93564-br,  14*10**-5],#1646_36 May01
        [np.pi*+90.0 / 180.0, 0.93601-br,  15*10**-5],#1732_17 May01
        [np.pi*+0.0 /  180.0, 0.93594-br,  21*10**-5],#1820_19 May01
        [np.pi*(-90.0+2.0) / 180.0, 0.93567-br,  6*10**-5],#2209_05 May01
        ])

data_500ma = np.array([
        [np.pi*(-90.0-2) / 180.0, 0.93597-br,  11*10**-5],#1057_17 May01
        [np.pi*+(90.0+2) / 180.0, 0.93595-br,  13*10**-5],#1732_17 May01
        ])


pyplot.figure()
pyplot.plot(np.linspace(-180,250,100),np.zeros_like(np.linspace(-180,250,100)),color = 'purple', linewidth = 3.0, linestyle = '--')
pyplot.errorbar(180.0 / np.pi * data[:,0], y = data[:,1], yerr = data[:,2], fmt = 'o', label = '1 A')
pyplot.errorbar(180.0 / np.pi * data_500ma[:,0], y = data_500ma[:,1], yerr = data_500ma[:,2], fmt = 'o', label = '0.5 A')
pyplot.errorbar(2.0, y = 0.93560-br, yerr = 15*10**-5, fmt = 'o', label = '3 A')#2019_58 May01
pyplot.errorbar(-2.0, y = 0.93558-br, yerr = 15*10**-5, fmt = 'o', label = '3 A, ortho. pol.')#2109_43 May01


pyplot.errorbar(4.0, y = 0.93565-br, yerr = 5e-5, fmt = 'o', label='1.9 A', color = 'purple') #our old measurement


#pyplot.xlabel('B field direction (deg)')
#pyplot.ylabel('Branching Fraction')


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
# pyplot.plot(180.0 / np.pi *sample, fitted)
pyplot.xlim(-180.0,250.0)
#pyplot.annotate('Amplitude {0:.2e}; Error {1:.2e}'.format(params['amplitude'].value, params['amplitude'].stderr), xy=(0.55, 0.90), xycoords='axes fraction')
pyplot.legend()
pyplot.show()