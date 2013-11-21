import numpy as np
import lmfit
from matplotlib import pyplot
import labrad

'This is a fit of narrow line spectrum of the carrier'

'''
define the function
'''
def gaussian_model(params, x):
    amplitude = params['amplitude'].value
    background_level = params['background_level'].value
    center = params['center'].value
    sigma = params['sigma'].value
    model =  background_level + amplitude * np.exp( - (x - center)**2 / (2 * sigma**2))
    return model
'''
define how to compare data to the function
'''
def gaussian_fit(params , x, data):
    model = gaussian_model(params, x)
    return model - data
'''
define the function
'''
def lorentzian_model(params, x):
    area = params['area'].value
    linewidth = params['linewidth'].value
    center = params['center'].value
    model =  (area / np.pi) * (linewidth / 2.0)**2 / ( ((linewidth / 2.0)**2) + (x - center)**2  )
    return model
'''
define how to compare data to the function
'''
def lorentzian_fit(params , x, data):
    model = lorentzian_model(params, x)
    return model - data


cxn = labrad.connect()
dv = cxn.data_vault
#change directory
directory = ('2013Jun05','1710_36')
dv.cd(['','Experiments','Spectrum729',directory[0],directory[1]])
dv.open(1)
data = dv.get().asarray
#get parameters
#line = dv.get_parameter('spectrum_saved_frequency')
#excitation_time = dv.get_parameter('excitation_time')[2]['us']

freqs = data[:,0] #frequency in real KHz
probs = data[:,1]

x_data = freqs
y_data = probs


'''
define the fitting parameters, with initial guesses. 
Here can also specify if some parameters are fixed, and the range of allowed values
'''
params = lmfit.Parameters()
params.add('area', value = 0.1, max=2.0)
params.add('center', value = -18.0)
params.add('linewidth', value = 0.001, min=0.0)
'''
run the fitting
'''
print x_data
result = lmfit.minimize(lorentzian_fit, params, args = (x_data, y_data))
'''
plot the result
'''
fit_values  = y_data + result.residual
x_fitted = np.arange(np.min(x_data)-params['center'].value,np.max(x_data)-params['center'].value,(np.max(x_data)-np.min(x_data))/1000)
y_fitted = lorentzian_model(params,np.arange(np.min(x_data),np.max(x_data),(np.max(x_data)-np.min(x_data))/1000))
pyplot.plot(x_fitted*1000, y_fitted, 'r', label = 'fitted',linewidth=3.0)
'''
plot the data
'''

pyplot.plot((x_data-params['center'].value)*1000, y_data, 'o', markersize = 8.0, label = 'data')

'''
print out fitting summary
'''
lmfit.report_errors(params)
pyplot.tick_params(axis='both', which='major', labelsize=20)
#pyplot.legend()
pyplot.show()