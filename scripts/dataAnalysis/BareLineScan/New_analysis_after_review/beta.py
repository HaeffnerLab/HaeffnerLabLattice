from __future__ import division
import numpy as np
from matplotlib import pyplot
from scipy import linalg
from scipy import special as bessel
import labrad
import lmfit


def beta_model(params, x1):
    A = params['A'].value
    B = params['B'].value
    #C = params['C'].value
    
    #x2 = np.array([0.574,0.726,0.918,1.161,1.353,1.560,1.754,1.998])
    
    #beta = np.sqrt(np.abs(A)/(x1)**4+np.abs(B)/(x1-0.596)**4+np.abs(C))
    #beta = np.sqrt(np.abs(A)/(x1)**4+np.abs(B)/(1.244*(x1-0.596))**4+np.abs(C))
    #beta = np.sqrt(np.abs(A)/(x1)**4+np.abs(B)/(1.18*(x1-0.530))**4)#+np.abs(C))#+np.abs(C))
    beta = np.sqrt((A/(x1)**2+B/(1.18*(x1-0.530))**2)**2)
    return beta
'''
define how to compare data to the function
'''
def beta_fit(params , x1, data, err):
    model = beta_model(params, x1)
    return (model - data)/err

x1 = np.array([1.07,1.19,1.3359,1.4744,1.681,1.851,2.0148,2.239])

x2 = np.array([0.574,0.726,0.918,1.161,1.353,1.560,1.754,1.998])

# beta = np.array([2.33,1.67,1.21,0.89,0.65,0.42,0.37,0.21])

beta = np.array([2.31,1.65,1.22,0.91,0.69,0.46,0.33,0.22])


#betaerr_for_fit = np.array([0.02,0.02,0.02,0.04,0.04,0.03,0.07,0.08])+2*beta*np.ones_like(x1)*0.05/x1
betaerr_for_fit = np.array([0.02,0.02,0.02,0.04,0.04,0.03,0.07,0.08])+2*beta*0.01
betaerr = np.array([0.02,0.02,0.02,0.04,0.04,0.03,0.07,0.08])

params = lmfit.Parameters()
params.add('A', value = 0.74,vary=True)
params.add('B', value = 0.68,vary=True)
#params.add('C', value = 0.01)

#x = (x1+x2)/2.0
#xerr = x*0.015

x = x1
xerr = 0.01*x1

result = lmfit.minimize(beta_fit, params, args = (x, beta, betaerr_for_fit))

fit_values  = beta + result.residual

lmfit.report_errors(params)

red_chi = result.redchi

print red_chi
#normalization = params['amplitude']/(params['gamma']/2.0)**2


pyplot.errorbar(x,beta,xerr=xerr,yerr=betaerr,linestyle='None',markersize = 7.0,fmt='o')
pyplot.plot(np.arange(1.0,2.3,0.01),beta_model(params,np.arange(1.0,2.3,0.01)),linewidth=2.0)
#pyplot.xlim((1.0,2.42))
#pyplot.ylim((0.5,3.51))
pyplot.show()