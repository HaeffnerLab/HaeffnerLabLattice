import matplotlib
import numpy as np

from matplotlib import pyplot
import lmfit

data = [
		[80, 0.935661264542],
		[79.5, 0.935661992802],
		[79, 0.935658585206],
		[78.5, 0.935656223057],
		[78.0, 0.93565648756],
		[77.5, 0.935653866836],
		[77.0, 0.93565184214],
		[76.5, 0.935649585317],
		[76.0, 0.935645321545],
		[75.5, 0.935639208811],
		[75.0, 0.935629967302],
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
params.add('amplitude', value = 1)
params.add('time_constant', value = 2)
params.add('background_level', value = 1)

result = lmfit.minimize(exponent_fit, params, args = (data[:,0],data[:,1]), **{'ftol':1e-30, 'xtol':1e-30} )
final  = data[:,1] + result.residual

predicted_level = params['background_level'].value

lmfit.report_errors(params)
correction = predicted_level - 0.935661264542
print correction, params['background_level'].stderr

pyplot.plot(data[:,0], data[:,1], '*')
pyplot.plot(sorted(data[:,0]), final, '-')
pyplot.show()