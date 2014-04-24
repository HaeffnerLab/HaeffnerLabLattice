from __future__ import division
import labrad
import numpy as np
from matplotlib import pyplot
import matplotlib
import lmfit

import lmfit

def cosine_model(params, x):
    A = params['A'].value
    freq = params['freq'].value
    phase=params['phase'].value
    offset=params['offset'].value
    output = A*np.cos(2*np.pi*x*freq+phase)+offset
    return output
'''
define how to compare data to the function
'''
def cosine_fit(params , x, data, err):
    model = cosine_model(params, x)
    return (model - data)/err



cxn = labrad.connect()
dv = cxn.data_vault

#change directory

figure = pyplot.figure(1)
figure.clf()


yerr = 1/np.sqrt(4*100)

x_13 = np.load('time_2014_04_13.npy')
y_13 = np.load('freq_2014_04_13.npy')
x_12 = np.load('time_2014_04_12.npy')
y_12 = np.load('freq_2014_04_12.npy')

x = np.append(x_12, x_13+86400)
y = np.append(y_12, y_13)

params = lmfit.Parameters()

params.add('A', value = 0.5)
params.add('freq', value = 1/(12*60*60), vary = False)
params.add('phase', value = 0.0)
params.add('offset', value = 0.0)

result = lmfit.minimize(cosine_fit, params, args = (x, y, yerr))

fit_values  = y + result.residual

lmfit.report_errors(params)

#pyplot.plot(time,phase,'o-')

x_plot = np.linspace(x.min(),x.max(),1000)

figure = pyplot.figure(1)
figure.clf()
#pyplot.plot(time,axial)
pyplot.plot(x,y,'o')
pyplot.plot(x_plot,cosine_model(params,x_plot),linewidth = 3.0)


pyplot.show()
