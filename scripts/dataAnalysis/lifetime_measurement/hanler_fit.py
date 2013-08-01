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
    offset = params['offset'].value
    asymmetry = params['asymmetry'].value
    
    #model =  amplitude*(1+gamma*(gamma*asymmetry+x)/(gamma**2+x**2))
    model =  amplitude*gamma*(asymmetry+x)/(gamma**2+x**2)+offset
    return model
'''
define how to compare data to the function
'''
def hanle_fit(params , x, data, err):
    model = hanle_model(params, x)
    return (model - data)/err




params = lmfit.Parameters()
params.add('amplitude', value = 800)
params.add('gamma', value = 22.4)
params.add('offset', value = 4000)
params.add('asymmetry', value = 0.17)

x_data = 0.93*2.4*(np.array([-8.3,0,3.13,9.01,11.11,6.04])-0.5) #11.1
y_err = np.array([108,109,107,104,105,106])
y_data = np.array([5220,4840,4120,3570,3920,3850]) #4120


result = lmfit.minimize(hanle_fit, params, args = (x_data, y_data, y_err))

fit_values  = y_data + result.residual
lmfit.report_errors(params)


#lmfit.report_errors(params)
pyplot.errorbar(x_data,y_data,y_err,ls='None',markersize = 3.0,fmt='o')
pyplot.plot(np.arange(-40,40,0.1),hanle_model(params,np.arange(-40,40,0.1)))
pyplot.show()