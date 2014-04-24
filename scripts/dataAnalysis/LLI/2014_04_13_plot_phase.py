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



# cxn = labrad.connect()
# dv = cxn.data_vault
# 
# #change directory
# 
# figure = pyplot.figure(1)
# figure.clf()
# 
# 
# dv.cd(['','Experiments','Ramsey2ions_ScanGapParity','2014Jan29','1756_34'])
# dv.cd(['','Drift_Tracking','LLI_tracking_all_data','2014Apr13'])
# dv.open(1)
# data = dv.get().asarray
data = np.load('2014_04_13_all_data.npy')
time = data[:,0]
 
ramsey_time = 0.098
 
where_early = np.where(time>69288)
where_late = np.where(time<21400)
# print time[0]
#time = time-time[0]
dataset = 9
phase = data[:,dataset]-np.average(data[:,dataset]) #3,7,9
 
time = np.append(time[where_early],time[where_late]+86400)
phase = np.append(phase[where_early],phase[where_late])
b_field = data[:,10]
axial = data[:,12]
b_field = np.append(b_field[where_early],b_field[where_late])
axial = np.append(axial[where_early],axial[where_late])
 
axial = (axial-np.average(axial))*1000*0.027*ramsey_time*360 ## convert to phase correction
b_field = ((b_field-np.average(b_field))*2*8/np.average(b_field))*ramsey_time*360 ## convert to phase correction
 
 
b_field_correction = True
axial_correction = True
if axial_correction:
    axial[np.where(axial<-0.7)] = np.ones_like(axial[np.where(axial<-0.7)])*np.average(axial)
    phase = phase - axial
if b_field_correction:
    phase = phase - b_field
     
time = time-time[0]



#x = np.load('time_2014_04_13.npy')
#y = np.load('freq_2014_04_13.npy')
x = time
y = phase/360/ramsey_time

#y = y + 0.084523*np.cos(2*np.pi*time*0.000049-2.985)
#y = y + 0.030584*np.cos(2*np.pi*time*0.000068-0.639967)

yerr = np.arcsin(1/np.sqrt(4*100)/0.35)/(2*np.pi*ramsey_time)
# yerr = 0.34
# x = np.load('time_binned_2014_04.npy')
# y = np.load('freq_binned_2014_04.npy')
# yerr = np.load('freq_err_2014_04.npy')

np.save('time_2014_04_13', x)
np.save('freq_2014_04_13', y)

params = lmfit.Parameters()

params.add('A', value = 0.05)
HR = 23.9344696
params.add('freq', value = 1/(HR*3600/2), vary = False)
params.add('phase', value = 0.0)
params.add('offset', value = 0.0)

result = lmfit.minimize(cosine_fit, params, args = (x, y, yerr))

fit_values  = y + result.residual

lmfit.report_errors(params)

print result.redchi

#pyplot.plot(time,phase,'o-')

x_plot = np.linspace(x.min(),x.max(),1000)

figure = pyplot.figure(1)
figure.clf()
#pyplot.plot(time,axial)
pyplot.plot(x,y,'o')
pyplot.plot(x_plot,cosine_model(params,x_plot),linewidth = 3.0)
#pyplot.xlabel("Seconds since 7:30 pm 4/14/2014")
#pyplot.ylabel("Frequency (Hz)")
amplitude = np.abs(params['A'].value*1000)
amplitude_error = params['A'].stderr*1000

#pyplot.annotate("Amplitude = {0:2.0f}".format(amplitude) + r'$\pm$' + "{0:2.0f} mHz".format(amplitude_error),xy=(20000,-1.2) )

#0.000049

pyplot.show()
