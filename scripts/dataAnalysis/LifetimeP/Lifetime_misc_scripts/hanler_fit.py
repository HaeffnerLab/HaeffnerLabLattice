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
params.add('amplitude', value = 420532)
params.add('gamma', value = 24, vary = False)
params.add('offset', value = 40000)
params.add('angle', value = 90*np.pi/180, vary = False)

x_data = (np.array([-12.833, -17.836, -22.813,10.7,7.32,12.24,17.016,21.696])) #11.1
y_err = np.array([215,214,217,220,200,200,200,200])
y_data = np.array([18250,17780,17220,20570,20233,21033,21058,20833]) #4120

result = lmfit.minimize(hanle_fit, params, args = (x_data, y_data, y_err))

fit_values  = y_data + result.residual
lmfit.report_errors(params)


#lmfit.report_errors(params)
pyplot.errorbar(x_data,y_data,y_err,ls='None',markersize = 3.0,fmt='o')
pyplot.plot(np.arange(-40,40,0.1),hanle_model(params,np.arange(-40,40,0.1)))
pyplot.show()