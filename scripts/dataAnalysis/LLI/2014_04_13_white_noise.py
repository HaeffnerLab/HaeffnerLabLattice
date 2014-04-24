from __future__ import division
import labrad
import numpy as np
from matplotlib import pyplot
import matplotlib
import lmfit



'''
Analyse the whole data set to see how gaussian the noise is
'''

def gaussian_model(params, x):
    A = params['A'].value
    width = params['width'].value
    center=params['center'].value
    output = A*np.exp(-(x-center)**2/(2*width**2))
    return output
'''
define how to compare data to the function
'''
def gaussian_fit(params , x, data, err):
    model = gaussian_model(params, x)
    return (model - data)/err

figure = pyplot.figure(1)
figure.clf()

#data = np.load('2014_04_13_all_data.npy')
time = np.load('time_2014_04_13.npy')
freq = np.load('freq_2014_04_13.npy')

#freq_diff = freq+0.019*np.cos(2*np.pi*time/(3600*12)+0.633362)-0.072616
freq_diff = freq - np.average(freq)
freq_histogram = np.histogram(freq_diff, 20)

x = freq_histogram[1][:-1]
y = freq_histogram[0]
yerr = np.sqrt(freq_histogram[0]+1)

params = lmfit.Parameters()
 
params.add('A', value = 140)
params.add('width', value = 0.2)
params.add('center', value = 0.0)
 
result = lmfit.minimize(gaussian_fit, params, args = (x, y, yerr))
 
fit_values  = y + result.residual
 
lmfit.report_errors(params)
 
print result.redchi

x_plot = np.linspace(x.min(),x.max(),1000)

pyplot.errorbar(x,y,yerr, linestyle='None',markersize = 4.0,fmt='o',color='black')
pyplot.plot(x_plot,gaussian_model(params,x_plot),linewidth = 3.0)
pyplot.show()
