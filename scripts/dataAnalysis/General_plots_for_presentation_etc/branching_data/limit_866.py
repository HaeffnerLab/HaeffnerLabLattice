import matplotlib
import numpy as np

from matplotlib import pyplot
import lmfit

data = [
		[100, 0.935663978181],
		[99, 0.935674649676],
		[98, 0.935686701014],
		[97, 0.935709059291],
		[96, 0.935740354076],
		[96.5, 0.935725431299],
		[97.5, 0.935695172986],
		[98.5, 0.935680300073],
		[99.5, 0.935669391782]
		]
data = np.array(sorted(data))

def exp_model(params, x):
	amplitude = params['amplitude'].value
	time_constant = params['time_constant'].value
	background_level = params['background_level'].value
	offset = x.min()
	model =  background_level + amplitude * np.exp( - (x - offset) / time_constant)
	return model

def exponent_fit(params , x, data):
	model = exp_model(params, x)
	return model - data

params = lmfit.Parameters()
params.add('amplitude', value = 10e-5, min = 0.0)
params.add('time_constant', value = 2, min = 0.0)
params.add('background_level', value = 1, min = 0.0)

result = lmfit.minimize(exponent_fit, params, args = (data[:,0],data[:,1]), **{'ftol':1e-30, 'xtol':1e-30}) 
final  = data[:,1] + result.residual

predicted_level = params['background_level'].value

lmfit.report_errors(params)
correction = predicted_level - 0.935663978181
print correction, params['background_level'].stderr

pyplot.plot(data[:,0], data[:,1], '*')
pyplot.plot(sorted(data[:,0]), final, '-')
pyplot.show()