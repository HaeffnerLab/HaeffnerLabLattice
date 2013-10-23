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
    offset= params['offset'].value
    #model =  amplitude*(1+gamma*(gamma*asymmetry+x)/(gamma**2+x**2))
    #model =  amplitude*gamma*(asymmetry+x)/(gamma**2+x**2)+offset
    model = amplitude*x/(gamma**2+(x)**2)+offset
    return model
'''
define how to compare data to the function
'''
def hanle_fit(params , x, data, err):
    model = hanle_model(params, x)
    return (model - data)/err




params = lmfit.Parameters()
params.add('amplitude', value = 2)
params.add('gamma', value = 10)
params.add('offset', value = 0.8)

x_data = (np.array([3.3,-3.3,-4.3,4.3,5.3])) #11.1
y_err = np.array([252,261,272,259,268])/10
y_data = np.array([0.831432,0.838103,0.8548,0.802863,0.8016477])*10000 #4120

result = lmfit.minimize(hanle_fit, params, args = (x_data, y_data, y_err))

fit_values  = y_data + result.residual
lmfit.report_errors(params)

contrast = params['amplitude'].value/params['offset'].value/params['gamma'].value/2
print 'contrast = ',contrast


#lmfit.report_errors(params)
pyplot.errorbar(x_data,y_data,y_err,ls='None',markersize = 3.0,fmt='o')
pyplot.plot(np.arange(-40,40,0.1),hanle_model(params,np.arange(-40,40,0.1)))
pyplot.show()