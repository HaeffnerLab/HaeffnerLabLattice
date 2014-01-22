import labrad
import numpy as np
from matplotlib import pyplot
import lmfit

def expo_model(params, x):
    amplitude = params['amplitude'].value
    time_offset = params['time_offset'].value
    amplitude_offset = params['amplitude_offset'].value
    decay_time = params['decay_time'].value
    model =  amplitude*np.exp(-(x-time_offset)/decay_time)-amplitude_offset
    return model

def expo_fit(params , x, data):
    model = expo_model(params, x)
    return model - data

data = np.genfromtxt("ring_down.csv",delimiter=",")

x_data = data[:,0]
y_data = data[:,1]

params = lmfit.Parameters()
params.add('amplitude', value = 6.0E-2)
params.add('time_offset', value = -1.5E-5)
params.add('amplitude_offset', value = 1E-2)
params.add('decay_time', value = 1.5E-5, min=0.0)

result = lmfit.minimize(expo_fit, params, args = (x_data, y_data))

fit_values  = y_data + result.residual

lmfit.report_errors(params)

x_data_theory = np.linspace(-1.18E-5,4.50E-5,10000)

print params['decay_time']*1000000

figure = pyplot.figure(1)
figure.clf()
pyplot.plot(x_data*1000000, y_data,'o',markersize = 3.0)
pyplot.plot(x_data_theory*1000000, expo_model(params,x_data_theory),'-',linewidth = 3.0)
#pyplot.plot(data[:,0], data[:,2],'o-')

pyplot.show()
