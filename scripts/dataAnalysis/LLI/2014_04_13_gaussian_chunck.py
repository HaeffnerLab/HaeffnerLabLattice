from __future__ import division
import labrad
import numpy as np
from matplotlib import pyplot
import matplotlib
import lmfit


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

def cosine_model(params, x):
    A = params['A'].value
    freq = params['freq'].value
    phase=params['phase'].value
    offset=params['offset'].value
    output = A*np.cos(2*np.pi*x*freq+phase)+offset#+B*x
    return output
'''
define how to compare data to the function
'''
def cosine_fit(params , x, data, err):
    model = cosine_model(params, x)
    return (model - data)/err



#data = np.load('2014_04_13_all_data.npy')
time = np.load('time_2014_04_13.npy')
freq = np.load('freq_2014_04_13.npy')

time_chunk = 8000
number_of_chunk = int(np.max(time)/time_chunk)
print number_of_chunk
offset = 8000
width_array = []
freq_array = []
time_array = []

for i in range(0,int(number_of_chunk*time_chunk/offset)):
    
    
    where = np.where((time>(i*offset))*(time<(i*offset+time_chunk)))
    time_stamp = (i+0.5)*offset
    time_array.append(time_stamp)
    freq_slice = freq[where]
    
    freq_array.append(np.average(freq_slice))
    
    freq_diff = freq_slice - np.average(freq_slice)
    freq_histogram = np.histogram(freq_diff, 10)
    
    x = freq_histogram[1][:-1]
    y = freq_histogram[0]
    yerr = np.sqrt(freq_histogram[0]+1)
    
    params = lmfit.Parameters()
     
    params.add('A', value = 140)
    params.add('width', value = 0.2)
    params.add('center', value = 0.0)
     
    result = lmfit.minimize(gaussian_fit, params, args = (x, y, yerr))
     
    fit_values  = y + result.residual
     
    #lmfit.report_errors(params)
    print "number of points =", np.size(freq_slice)
    print "width =", params['width'].value, 'Chi = ', result.redchi
    width_array.append(np.abs(params['width'].value)/np.sqrt(np.size(freq_slice)))
    #print 'Chi = ', result.redchi
    
    x_plot = np.linspace(x.min(),x.max(),1000)
    
    figure = pyplot.figure(i)
    figure.clf()
      
    pyplot.errorbar(x,y,yerr, linestyle='None',markersize = 4.0,fmt='o',color='black')
    pyplot.plot(x_plot,gaussian_model(params,x_plot),linewidth = 3.0)
 
# width_array = width_array - np.average(width_array)    
# width_histogram = np.histogram(width_array,20)
# 
# x = width_histogram[1][:-1]
# y = width_histogram[0]
# yerr = np.sqrt(width_histogram[0]+1)
# 
# print x
# print y
# 
# params = lmfit.Parameters()
#  
# params.add('A', value = 0.2)
# params.add('width', value = 0.2)
# params.add('center', value = 0.0)
#  
# result = lmfit.minimize(gaussian_fit, params, args = (x, y, yerr))
#  
# fit_values  = y + result.residual
# 
# lmfit.report_errors(params)
# 
# x_plot = np.linspace(x.min(),x.max(),1000)
# 
# pyplot.errorbar(x,y,yerr, linestyle='None',markersize = 4.0,fmt='o',color='black')
# pyplot.plot(x_plot,gaussian_model(params,x_plot),linewidth = 3.0)

x = np.array(time_array)
y = np.array(freq_array)
yerr = np.array(width_array)

params = lmfit.Parameters()

params.add('A', value = 0.5)
params.add('freq', value = 1/(6*3600), vary = False)
params.add('phase', value = 0.0)
params.add('offset', value = 0.0)

result = lmfit.minimize(cosine_fit, params, args = (x, y, yerr))

fit_values  = y + result.residual

lmfit.report_errors(params)

#print result.redchi

#print 1/params['freq'].value/3600

x_plot = np.linspace(x.min(),x.max(),1000)

figure = pyplot.figure(i+1)
figure.clf()

pyplot.plot(x,y,'o')
pyplot.plot(x_plot,cosine_model(params,x_plot),linewidth = 3.0)
pyplot.errorbar(time_array,freq_array,width_array, linestyle='None',markersize = 4.0,fmt='o',color='black')

    
pyplot.show()


'''
bin chunk = 1000: 31(27) mHz
bin chunk = 2000: 43(27) mHz
bin chunk = 4000: 37(49) mHz
bin chunk = 6000: 17(49) mHz
bin chunk = 8000: 51(91) mHz
'''

'''
105(13) mHz, phase = 0.78 --> 5.96 hrs
89(10) mHz, phase = 0.059 --> 5.578 hrs
'''
