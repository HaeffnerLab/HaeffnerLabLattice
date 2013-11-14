import numpy as np
import lmfit
from matplotlib import pyplot
import labrad

'This is a fit of narrow line spectrum of the carrier'

'''
define the function
'''
def hanle_model(params, x):
    p = params['p'].value
    amplitude = params['amplitude'].value
    gamma = params['gamma'].value
    offset= params['offset'].value
    Delta= params['Delta'].value
    #model =  amplitude*(1+gamma*(gamma*asymmetry+x)/(gamma**2+x**2))
    #model =  amplitude*gamma*(asymmetry+x)/(gamma**2+x**2)+offset
    #model = -amplitude*x/(gamma**2+(x)**2)+offset
    model = amplitude*(2.0*x*(gamma**2+2*(2*Delta**2-6*(p-1)*Delta*x+(5+p)*x**2)))/(gamma**4+2*gamma**2*(4*Delta**2+(10+p)*x**2)+4*(4*Delta**4-2*(8+p)*Delta**2*x**2+5*(5+p)*x**4))+offset
    return model
'''
define how to compare data to the function
'''
def hanle_fit(params , x, data, err):
    model = hanle_model(params, x)
    return (model - data)/err




params = lmfit.Parameters()
params.add('p', value = 0.9)
params.add('amplitude', value = 253000)
params.add('gamma', value = 10)
params.add('offset', value = 60000)
params.add('Delta', value = 15)

x_data = (np.array([-1.0,-2.0,-3.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,11.0,12.0,9.50,-9.50,-8.00])) #11.1
y_err = np.array([344,344,344,344,344,344,344,344,344,344,344,344,344,344,344])
y_data = np.array([53559,52802,50896,57761,60047,62634,65488,69619,73927,77290,73090,71110,76802,36572,41076])

#x_data = (np.array([3.0,4.0,5.0,6.0,7.0,8.0,9.0,11.0,12.0,9.50])) #11.1
#y_err = np.array([344,344,344,344,344,344,344,344,344,344])
#y_data = np.array([57761,60047,62634,65488,69619,73927,77290,73090,71110,76802])

result = lmfit.minimize(hanle_fit, params, args = (x_data, y_data, y_err))

fit_values  = y_data + result.residual
lmfit.report_errors(params)

#contrast = params['amplitude'].value/params['offset'].value/params['gamma'].value/2
#print 'contrast = ',contrast


lmfit.report_errors(params)
pyplot.errorbar(x_data,y_data,y_err,ls='None',markersize = 3.0,fmt='o')
pyplot.plot(np.arange(-20,20,0.1),hanle_model(params,np.arange(-20,20,0.1)))
pyplot.show()