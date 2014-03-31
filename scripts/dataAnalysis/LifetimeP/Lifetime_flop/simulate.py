import numpy as np
import lmfit
from matplotlib import pyplot
import labrad

'This is a fit of narrow line spectrum of the carrier'

'''
define the function
'''
def decay_model(params, x):
    T2 = params['T2'].value
    freq = params['freq'].value
    t = x
    model =  0.5*np.exp(-t/T2)*np.sin(2*np.pi*freq*t)
    return model
'''
define how to compare data to the function
'''
def decay_fit(params , x, data, err):
    model = decay_model(params, x)
    return (model - data)/err

stop_time = 0.01
start_time = 0.001
x_data = np.linspace(start_time,stop_time,100)
x_data_theory = np.linspace(start_time,stop_time,1000)

result_freq = 0.0
result_freq_error = 0.0
result_T2 = 0.0
result_T2_error = 0.0
k=1000
target_T2 = 0.005
target_freq = 1000

for i in range(0,k):
    params = lmfit.Parameters()
    params.add('T2', value = target_T2)
    params.add('freq', value = target_freq)

    'generate data'
    y_center = decay_model(params,x_data)
    N = 500
    y_err = np.sqrt((1-y_center**2)/(4*N))
    y_data = np.random.normal(y_center,y_err)

    '''
    run the fitting
    '''
    result = lmfit.minimize(decay_fit, params, args = (x_data, y_data, y_err))
    '''
    plot the result
    '''
    fit_values  = y_data + result.residual
#lmfit.report_errors(params)
    result_freq += params['freq']
    result_T2 += params['T2']
    result_freq_error += (params['freq']-target_freq)/target_freq
    result_T2_error += (params['T2']-target_T2)/target_T2

print 'freq error is ', result_freq_error/k
print 'T2 error is ', result_T2_error/k

#lmfit.report_errors(params)
pyplot.errorbar(x_data,y_data,y_err,ls='None',markersize = 3.0,fmt='o')
pyplot.plot(x_data_theory,decay_model(params,x_data_theory))
pyplot.show()