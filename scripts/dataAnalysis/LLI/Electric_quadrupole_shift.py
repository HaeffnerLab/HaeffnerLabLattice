from __future__ import division
import numpy as np
from matplotlib import pyplot
from scipy import linalg
from scipy import special as bessel
import labrad
import lmfit


def linear_model(params, x1):
    A = params['A'].value
    B = params['B'].value

    
    #x2 = np.array([0.574,0.726,0.918,1.161,1.353,1.560,1.754,1.998])
    
    #y = x1**2*A + B
    y = x1*A + B
    
    return y
'''
define how to compare data to the function
'''
def linear_fit(params , x1, data, err):
    model = linear_model(params, x1)
    return (model - data)/err

#x1 = np.array([1.07,1.19,1.3359,1.4744,1.681,1.851,2.0148,2.239])

#x2 = np.array([0.574,0.726,0.918,1.161,1.353,1.560,1.754,1.998])

x1 = np.array([176,214.7,248.7,281.6,331])
#x1 = np.array([176,214.7,248.7,281.6,331])

y1 = np.array([305.6,241.3,202.7,181,155.3])
y1_err = np.array([0.5,0.4,0.5,1.0,0.9])
y2 = np.array([326.2,265.2,230.0,210.1,185.8])
y2_err = np.array([0.7,0.4,0.5,0.4,0.6])
y_err = np.sqrt(y1_err**2+y2_err**2)
#y_err = y1_err+y2_err
y = (y2-y1)/2.0

electron_charge = 1.60e-19
calcium_mass = 40 * 1.66e-27

y = y[:]
x1 = x1[:]
#x1 = x1**2
x1 = x1**2#*calcium_mass/electron_charge ##converted to V/mm^2
y_err = y_err[:]

params = lmfit.Parameters()
params.add('A', value = 1.0)
params.add('B', value = 0.0)



xerr = np.ones_like(x1)*0.02

result = lmfit.minimize(linear_fit, params, args = (x1, y, y_err))

fit_values  = y + result.residual

lmfit.report_errors(params)

red_chi = np.sum(result.residual**2)/(np.size(x1)-2)

#print red_chi

print params['A'].value

#normalization = params['amplitude']/(params['gamma']/2.0)**2


pyplot.errorbar(x1,y,y_err,linestyle='None',markersize = 7.0,fmt='o')
pyplot.plot(np.arange(0,np.max(x1),0.01),linear_model(params,np.arange(0,np.max(x1),0.01)),linewidth=2.0)
#pyplot.xlim((0.0,2))
#pyplot.ylim((0,18))
#pyplot.xlabel('Axial trap freq (kHz)')
#pyplot.xlabel('E-gradient (V/mm^2)')
#pyplot.ylabel('Oscillation freq (Hz)')
#pyplot.annotate('Hello')
pyplot.show()