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
    #asymmetry = params['asymmetry'].value
    
    model =  amplitude*gamma*x/(gamma**2+x**2)
    return model
'''
define how to compare data to the function
'''
def hanle_fit(params , x, data, err):
    model = hanle_model(params, x)
    return (model - data)/err

x_data = np.array([5,10,15,20,25])

result_error = 0.0
result_gamma = 0.0
k=1000

for i in range(0,k):
    params = lmfit.Parameters()
    params.add('amplitude', value = 100000)
    params.add('gamma', value = 22.416)

    'generate data'
    y_center = hanle_model(params,x_data)
    y_err = np.sqrt(y_center)
    y_data = np.random.normal(y_center,y_err)

    '''
    run the fitting
    '''
    result = lmfit.minimize(hanle_fit, params, args = (x_data, y_data, y_err))
    '''
    plot the result
    '''
    fit_values  = y_data + result.residual
#lmfit.report_errors(params)
    result_gamma += params['gamma']
    result_error += params['gamma'].stderr/params['gamma']

print 'gamma is ', result_gamma/(k)
print result_error/(k)

lmfit.report_errors(params)
pyplot.errorbar(x_data,y_data,y_err,ls='None',markersize = 3.0,fmt='o')
pyplot.plot(np.arange(0,50,0.1),hanle_model(params,np.arange(0,50,0.1)))
pyplot.show()