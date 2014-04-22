from __future__ import division
import labrad
import numpy as np
from matplotlib import pyplot
import matplotlib
import lmfit
import datetime

def cosine_model(params, x):
    freq = 1/(sidereal_day*3600) ## this is omega t
    A = params['A'].value
    B = params['B'].value
    C = params['C'].value
    D = params['D'].value
    offset=params['offset'].value
    output = A*np.cos(2*np.pi*x*freq)+B*np.sin(2*np.pi*x*freq)+C*np.cos(2*np.pi*x*2*freq)+D*np.sin(2*np.pi*x*2*freq)+offset
    return output
'''
define how to compare data to the function
'''
def cosine_fit(params , x, data, err):
    model = cosine_model(params, x)
    return (model - data)/err



data = np.load('2014_04_13_all_data.npy')
time = data[:,0]

ramsey_time = 0.098

where_early = np.where(time>69288)
where_late = np.where(time<21400)
time = np.append(time[where_early],time[where_late]+86400)

### time conversion ####
# data starts on April 13, 2014, 69297.0 Berkeley time
Berkeley_longitude = 122.2728/360
sidereal_day = 23.9344699 ### in hours
### UTC is faster than Berkeley time
offset_from_UTC = Berkeley_longitude*sidereal_day*60*60
### add offset to data
time = time + offset_from_UTC - 86400 ## Now becomes seconds since April 14 UTC time
# April 13, 2014 at midnight Berkeley is 
# 2014 equinox is March 20 16:57:06 UTC, which is 
equinox = datetime.datetime(2014, 3, 20, 16, 57, 6)
experiment_day = datetime.datetime(2014, 4, 15, 00, 00, 00)
time_difference = experiment_day - equinox
### convert time to seconds since equinox
time = time + time_difference.total_seconds()
#### end of time conversion ####

### get phase data and correction from axial trap and B-field ###
dataset = 9
phase = data[:,dataset]-np.average(data[:,dataset]) #3,7,9

phase = np.append(phase[where_early],phase[where_late])
b_field = data[:,10]
axial = data[:,12]
b_field = np.append(b_field[where_early],b_field[where_late])
axial = np.append(axial[where_early],axial[where_late])
 
axial = (axial-np.average(axial))*1000*0.027*ramsey_time*360 ## convert to phase correction 27 mHz per kHz
b_field = ((b_field-np.average(b_field))*2*8/np.average(b_field))*ramsey_time*360 ## convert to phase correction 8 Hz at 3.9 gauss
 
#### apply correction due to B-field and axial trap frequency ####
 
b_field_correction = True
axial_correction = True
if axial_correction:
    axial[np.where(axial<-0.7)] = np.ones_like(axial[np.where(axial<-0.7)])*np.average(axial)
    phase = phase - axial
if b_field_correction:
    phase = phase - b_field

x = time
y = phase/360/ramsey_time

np.save('2014_04_13_time.npy',x)
np.save('2014_04_13_freq.npy',y)
## assume quantum projection noise
yerr = np.arcsin(1/np.sqrt(4*100)/0.35)/(2*np.pi*ramsey_time)

params = lmfit.Parameters()

params.add('A', value = 0, vary = True) ##cos ### -3 cXZ sin 2 chi: 7 +- 23 mHz
params.add('B', value = 0, vary = True) ##sin ### -3 cYZ sin 2 chi: 32 +- 56 mHz
params.add('C', value = 0, vary = True) ##cos2 ### -1.5 (cXX-cYY) sin^2 chi: 15 +- 22 mHz
params.add('D', value = 0, vary = True) ##sin2 ### -3 cXY sin^2 chi: 8 +- 20 mHz
params.add('offset', value = 0.069818)

result = lmfit.minimize(cosine_fit, params, args = (x, y, yerr))

fit_values  = y + result.residual

lmfit.report_errors(params)

print "Reduced chi-squared = ", result.redchi

ci = lmfit.conf_interval(result)

lmfit.report_ci(ci)

x_plot = np.linspace(x.min(),x.max()+100000,1000)

figure = pyplot.figure(1)
figure.clf()
pyplot.plot(x,y,'o')
pyplot.plot(x_plot,cosine_model(params,x_plot),linewidth = 3.0)
pyplot.show()