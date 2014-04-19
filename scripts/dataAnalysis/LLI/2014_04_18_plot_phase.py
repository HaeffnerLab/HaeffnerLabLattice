from __future__ import division
import labrad
import numpy as np
from matplotlib import pyplot
import matplotlib
import lmfit

import lmfit

def cosine_model(params, x):
    freq = 1/(23.9344699*3600) ## this is omega t
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



cxn = labrad.connect()
dv = cxn.data_vault

#change directory

figure = pyplot.figure(1)
figure.clf()


#dv.cd(['','Experiments','Ramsey2ions_ScanGapParity','2014Jan29','1756_34'])
dv.cd(['','Drift_Tracking','LLI_tracking_all_data','2014Apr18'])
dv.open(1)
data = dv.get().asarray
time = data[:,0]

ramsey_time = 0.095
axial = (data[:,12]-np.average(data[:,12]))*1000*0.027*ramsey_time*360 ## convert to phase
fractional_b_field = (data[:,10]-np.average(data[:,10]))/np.average(data[:,10])
            
b_field = fractional_b_field*2*8*ramsey_time*360

#time = time-time[0]
#3 = average phase long time
#7 = average phase short time
#9 = average phase difference
dataset = 9
phase = data[:,dataset]-np.average(data[:,dataset]) #3,7,9

skip = 0

time = time[skip:]
axial = axial[skip:]
b_field = b_field[skip:]
phase = phase[skip:]

where_early = np.where(time>73500)#73000,67200
where_late = np.where(time<32476)


time = np.append(time[where_early],time[where_late]+86400)
phase = np.append(phase[where_early],phase[where_late])
b_field = np.append(b_field[where_early],b_field[where_late])
axial = np.append(axial[where_early],axial[where_late])

b_field_correction = True
axial_correction = True
if axial_correction:
    #axial[np.where(axial<-0.7)] = np.ones_like(axial[np.where(axial<-0.7)])*np.average(axial)
    phase = phase - axial
if b_field_correction:
    phase = phase - b_field

time = time-time[0]



x = time
phase = phase - np.average(phase)
y = phase/360/ramsey_time
#y = b_field
yerr = np.arcsin(1/np.sqrt(4*100)/0.35)/(2*np.pi*ramsey_time)

# x = np.load('time_binned_2014_04_16.npy')
# y = np.load('freq_binned_2014_04_16.npy')
# yerr = np.load('freq_err_2014_04_16.npy')

#np.save('time_2014_04_16', x)
#np.save('freq_2014_04_16', y)

params = lmfit.Parameters()

params.add('A', value = 0, vary = True) ##cos ### -3 cXZ sin 2 chi: 7 +- 23 mHz
params.add('B', value = 0, vary = True) ##sin ### -3 cYZ sin 2 chi: 32 +- 56 mHz
params.add('C', value = 0, vary = True) ##cos2 ### -1.5 (cXX-cYY) sin^2 chi: 15 +- 22 mHz
params.add('D', value = 0, vary = True) ##sin2 ### -3 cXY sin^2 chi: 8 +- 20 mHz
params.add('offset', value = 0.069818)

result = lmfit.minimize(cosine_fit, params, args = (x, y, yerr))

fit_values  = y + result.residual

lmfit.report_errors(params)

print result.redchi

#pyplot.plot(time,phase,'o-')

x_plot = np.linspace(x.min(),x.max()*2,1000)

figure = pyplot.figure(1)
figure.clf()
#pyplot.plot(time,axial)
pyplot.plot(x,y,'o')
pyplot.plot(x_plot,cosine_model(params,x_plot),linewidth = 3.0)


pyplot.show()
