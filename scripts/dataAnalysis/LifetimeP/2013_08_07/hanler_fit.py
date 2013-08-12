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
    angle= params['angle'].value
    #model =  amplitude*(1+gamma*(gamma*asymmetry+x)/(gamma**2+x**2))
    #model =  amplitude*gamma*(asymmetry+x)/(gamma**2+x**2)+offset
    model = amplitude*(gamma*np.cos(angle)+x*np.sin(angle))/(gamma**2+(x)**2)+offset
    return model
'''
define how to compare data to the function
'''
def hanle_fit(params , x, data, err):
    model = hanle_model(params, x)
    return (model - data)/err




params = lmfit.Parameters()
params.add('amplitude', value = -34600)
params.add('gamma', value = 10, vary = False)
params.add('offset', value = 8264)
params.add('angle', value = 90*np.pi/180, vary = False)

x_data = (np.array([6,8,4,11,3,2,-3,-6,-9.98,-11.79,0])) #11.1
y_err = np.array([114,113,115,113,117,118,118,121,122,120,117])
y_data = np.array([7043,6792,7298,6754,7624,7572,8008,8621,8914,8877,7847]) #4120

result = lmfit.minimize(hanle_fit, params, args = (x_data, y_data, y_err))

fit_values  = y_data + result.residual
lmfit.report_errors(params)


#lmfit.report_errors(params)
pyplot.errorbar(x_data,y_data,y_err,ls='None',markersize = 3.0,fmt='o')
pyplot.plot(np.arange(-40,40,0.1),hanle_model(params,np.arange(-40,40,0.1)))
pyplot.show()