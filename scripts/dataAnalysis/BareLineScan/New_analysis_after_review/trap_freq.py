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

x1 = np.array([1.3359,1.4744,1.681,1.851,2.0148,2.239])

x2 = np.array([0.918,1.161,1.353,1.560,1.754,1.998])

x1_err = x1*0.04


params = lmfit.Parameters()
params.add('A', value = 0.47)
params.add('B', value = -0.52)



x = x1
xerr = np.ones_like(x1)*0.02

result = lmfit.minimize(linear_fit, params, args = (x1, x2, x1_err))

fit_values  = x2 + result.residual

lmfit.report_errors(params)

#normalization = params['amplitude']/(params['gamma']/2.0)**2


pyplot.errorbar(x1,x2,xerr=x1*0.02,yerr=x2*0.02,linestyle='None',markersize = 7.0,fmt='o')
pyplot.plot(np.arange(1.3,2.3,0.01),linear_model(params,np.arange(1.3,2.3,0.01)),linewidth=2.0)
#pyplot.xlim((1.0,2.42))
#pyplot.ylim((0.5,3.51))
pyplot.show()