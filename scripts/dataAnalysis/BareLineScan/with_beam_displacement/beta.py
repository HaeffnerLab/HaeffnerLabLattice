from __future__ import division
import numpy as np
from matplotlib import pyplot
from scipy import linalg
from scipy import special as bessel
import labrad
import lmfit


def beta_model(params, x1):
    A = params['A'].value
    C = params['C'].value
    
    #x2 = np.array([0.918,1.161,1.353,1.560,1.754,1.998])
    
    #beta = np.sqrt(np.absolute((A/x1**2+B/x2**2)**2+C))
    beta = np.sqrt(A/x1**4+C)
    
    return beta
'''
define how to compare data to the function
'''
def beta_fit(params , x1, data, err):
    model = beta_model(params, x1)
    return (model - data)/err

x1 = np.array([1.3359,1.4744,1.681,1.851,2.0148,2.239])

x2 = np.array([0.918,1.161,1.353,1.560,1.754,1.998])

beta = np.array([2.65,2.04,1.59,1.22,0.99,0.70])


betaerr_for_fit = np.array([0.01,0.01,0.01,0.01,0.02,0.03])+beta*0.03
betaerr = np.array([0.01,0.01,0.01,0.01,0.02,0.03])*1.5

params = lmfit.Parameters()
params.add('A', value = 12.0)
params.add('C', value = 0.0)

x = (x1+x2)/2.0
xerr = x*0.015

result = lmfit.minimize(beta_fit, params, args = (x, beta, betaerr_for_fit))

fit_values  = beta + result.residual

lmfit.report_errors(params)

#normalization = params['amplitude']/(params['gamma']/2.0)**2


pyplot.errorbar(x,beta,xerr=xerr,yerr=betaerr,linestyle='None',markersize = 7.0,fmt='o')
pyplot.plot(np.arange(1.0,2.4,0.01),beta_model(params,np.arange(1.0,2.4,0.01)),linewidth=2.0)
pyplot.xlim((1.0,2.42))
pyplot.ylim((0.5,3.51))
pyplot.show()