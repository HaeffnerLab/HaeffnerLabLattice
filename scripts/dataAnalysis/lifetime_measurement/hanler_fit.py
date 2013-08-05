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
    angle = params['angle'].value
    polarization = params['polarization'].value
    #offset= params['offset'].value
    #model =  amplitude*(1+gamma*(gamma*asymmetry+x)/(gamma**2+x**2))
    #model =  amplitude*gamma*(asymmetry+x)/(gamma**2+x**2)+offset
    model = amplitude*(1/gamma)*(2.0+polarization*np.cos(angle))+amplitude*(2.0/3.0)*np.sin(angle)*polarization*(x)/(gamma**2+(x)**2)
    return model
'''
define how to compare data to the function
'''
def hanle_fit(params , x, data, err):
    model = hanle_model(params, x)
    return (model - data)/err




params = lmfit.Parameters()
params.add('amplitude', value = 160907)
params.add('gamma', value = 6.551361)
params.add('polarization', value = 1, vary = False)
params.add('angle', value = 90*np.pi/180, vary = False)
#params.add('offset', value = 0.5)

x_data = (np.array([1.063,3.05,5.10,7.09, 9.04,-4.00,-1.067])) #11.1
y_err = np.array([315,326,329,334,334,320,325])
y_data = np.array([45520,48560,50480,50540,50000,43770,47920]) #4120

result = lmfit.minimize(hanle_fit, params, args = (x_data, y_data, y_err))

fit_values  = y_data + result.residual
lmfit.report_errors(params)


#lmfit.report_errors(params)
pyplot.errorbar(x_data,y_data,y_err,ls='None',markersize = 3.0,fmt='o')
pyplot.plot(np.arange(-40,40,0.1),hanle_model(params,np.arange(-40,40,0.1)))
pyplot.show()