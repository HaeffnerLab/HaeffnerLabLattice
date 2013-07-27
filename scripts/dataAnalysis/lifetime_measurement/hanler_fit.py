import numpy as np
import lmfit
from matplotlib import pyplot
import labrad

'This is a fit of narrow line spectrum of the carrier'

'''
define the function
'''
def hanle_model(params, x):
    amplitude = params['amplitude'].value
    gamma = params['gamma'].value
    asymmetry = params['asymmetry'].value
    
    model =  amplitude*(1+gamma*(gamma*asymmetry+x)/(gamma**2+x**2))
    return model
'''
define how to compare data to the function
'''
def hanle_fit(params , x, data, err):
    model = hanle_model(params, x)
    return (model - data)/err




params = lmfit.Parameters()
params.add('amplitude', value = 500)
params.add('gamma', value = 22.416)
params.add('asymmetry', value = 0.0, vary = False)

x_data = np.array([-19.2,-1,1,19.2])
y_err = np.array([50,50,50,50])
y_data = np.array([705,784,804,856])


result = lmfit.minimize(hanle_fit, params, args = (x_data, y_data, y_err))

fit_values  = y_data + result.residual
lmfit.report_errors(params)


#lmfit.report_errors(params)
pyplot.errorbar(x_data,y_data,y_err,ls='None',markersize = 3.0,fmt='o')
pyplot.plot(np.arange(-40,40,0.1),hanle_model(params,np.arange(-40,40,0.1)))
pyplot.show()