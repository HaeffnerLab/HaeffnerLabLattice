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

betaerr = np.ones_like(x1)*0.03

params = lmfit.Parameters()
params.add('A', value = 12.0)
params.add('C', value = 0.0)

x1 = (x1+x2)/2.0

result = lmfit.minimize(beta_fit, params, args = (x1, beta, betaerr))

fit_values  = beta + result.residual

lmfit.report_errors(params)

#normalization = params['amplitude']/(params['gamma']/2.0)**2


pyplot.errorbar(x1,beta,betaerr,linestyle='None',markersize = 3.0,fmt='o')
pyplot.plot(np.arange(1.0,2.4,0.01),beta_model(params,np.arange(1.0,2.4,0.01)))
pyplot.show()