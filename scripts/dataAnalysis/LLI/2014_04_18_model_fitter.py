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

cxn = labrad.connect()
dv = cxn.data_vault

####### common variable ######

ramsey_time = 0.095
Berkeley_longitude = 122.2728/360
sidereal_day = 23.9344699 ### in hours
### UTC is faster than Berkeley time
offset_from_UTC = Berkeley_longitude*sidereal_day*60*60
equinox = datetime.datetime(2014, 3, 20, 16, 57, 6)
## which phase?
dataset = 9


######################## DAY 1 start ##############    

dv.cd(['','Drift_Tracking','LLI_tracking_all_data','2014Apr18'])
dv.open(1)
data = dv.get().asarray

time = data[:,0]



where_early = np.where(time>73500)
where_late = np.where(time<32476)
time = np.append(time[where_early],time[where_late]+86400)

### time conversion ####
# data starts on April 13, 2014, 69297.0 Berkeley time
### UTC is faster than Berkeley time
### add offset to data
time = time + offset_from_UTC - 86400 ## Now becomes seconds since April 19 UTC time
# April 13, 2014 at midnight Berkeley is 
# 2014 equinox is March 20 16:57:06 UTC, which is 
experiment_day = datetime.datetime(2014, 4, 19, 00, 00, 00)
time_difference = experiment_day - equinox
### convert time to seconds since equinox
time = time + time_difference.total_seconds()
#### end of time conversion ####

### get phase data and correction from axial trap and B-field ###

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
    
x1 = time
y1 = phase/360/ramsey_time
    
######################## DAY 1 end ##############    

######################## DAY 2 start ##############    

dv.cd(['','Drift_Tracking','LLI_tracking_all_data','2014Apr19'])
dv.open(1)
data = dv.get().asarray

time = data[:,0]


where_early = np.where(time>34000)
where_late = np.where(time<20000)
time = np.append(time[where_early],time[where_late]+86400)

### time conversion ####
# data starts on April 13, 2014, 69297.0 Berkeley time

### add offset to data
time = time + offset_from_UTC - 86400 ## Now becomes seconds since April 19 UTC time
# April 13, 2014 at midnight Berkeley is 
# 2014 equinox is March 20 16:57:06 UTC, which is 
experiment_day = datetime.datetime(2014, 4, 20, 00, 00, 00)
time_difference = experiment_day - equinox
### convert time to seconds since equinox
time = time + time_difference.total_seconds()
#### end of time conversion ####

### get phase data and correction from axial trap and B-field ###
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
    
x2 = time
y2 = phase/360/ramsey_time
    
######################## DAY 2 end ##############  


### add 2 days of data together ###

x = np.append(x1,x2)
y = np.append(y1,y2)

np.save('2014_04_18_weekend_freq.npy',y)
np.save('2014_04_18_weekend_time.npy',x)

## assume quantum projection noise
yerr = np.arcsin(1/np.sqrt(4*100)/0.35)/(2*np.pi*ramsey_time)

params = lmfit.Parameters()

params.add('A', value = 0, vary = True) ##cos ### -3 cXZ sin 2 chi: 7 +- 23 mHz
params.add('B', value = 0, vary = True) ##sin ### -3 cYZ sin 2 chi: 32 +- 56 mHz
params.add('C', value = 0, vary = True) ##cos2 ### -1.5 (cXX-cYY) sin^2 chi: 15 +- 22 mHz
params.add('D', value = 0, vary = True) ##sin2 ### -3 cXY sin^2 chi: 8 +- 20 mHz
params.add('offset', value = 0.0)

result = lmfit.minimize(cosine_fit, params, args = (x, y, yerr))

residual_array = result.residual*yerr

#fit_values  = y + result.residual

lmfit.report_errors(params)

print "Reduced chi-squared = ", result.redchi

ci = lmfit.conf_interval(result)
# report confidence interval
#lmfit.report_ci(ci)

x_plot = np.linspace(x.min(),x.max()+100000,1000)

### plot phase data and fit model ###
figure = pyplot.figure(1)
figure.clf()
pyplot.plot(x,y,'o')
pyplot.plot(x_plot,cosine_model(params,x_plot),linewidth = 3.0)

### plot residual histogram and fit to gaussian

residual_histogram = np.histogram(residual_array,15)
x = residual_histogram[1][:-1]
y = residual_histogram[0]
##
yerr = np.sqrt(residual_histogram[0])

yerr[np.where(yerr<=0.0)] = np.ones_like(yerr[np.where(yerr<=0.0)])

params = lmfit.Parameters()
 
params.add('A', value = 140)
params.add('width', value = 0.2)
params.add('center', value = 0.0)


figure = pyplot.figure(2)
figure.clf()
result = lmfit.minimize(gaussian_fit, params, args = (x, y, yerr))
 
fit_values  = y + result.residual
 
lmfit.report_errors(params)
 
print "Reduced chi-squared Gaussian = ", result.redchi

x_plot = np.linspace(x.min(),x.max(),1000)

pyplot.errorbar(x,y,yerr, linestyle='None',markersize = 4.0,fmt='o',color='black')
pyplot.plot(x_plot,gaussian_model(params,x_plot),linewidth = 3.0)
pyplot.show()