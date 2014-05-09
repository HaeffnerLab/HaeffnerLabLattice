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


#dv.cd(['','Experiments','Ramsey2ions_ScanGapParity','2014Jan29','1756_34'])
dv.cd(['','Drift_Tracking','LLI_tracking_all_data','2014Apr13'])
dv.open(1)
data = dv.get().asarray
time = data[:,0]

ramsey_time = 0.098

where_early = np.where(time>69288)
where_late = np.where(time<21400)
#time = time-time[0]
dataset = 9
phase = data[:,dataset]-np.average(data[:,dataset]) #3,7,9

time = np.append(time[where_early],time[where_late]+86400)
phase = np.append(phase[where_early],phase[where_late])
b_field = data[:,10]
print np.average(b_field)
b_field = np.append(b_field[where_early],b_field[where_late])


b_field_freq = ((b_field-np.average(b_field))*2*8/np.average(b_field))

time = time-time[0]

x = time
y = b_field_freq
yerr = 1/np.sqrt(4*100)


params = lmfit.Parameters()

params.add('A', value = 0.5)
params.add('freq', value = 1/(3600*12), vary = False)
params.add('phase', value = 0.0)
params.add('offset', value = 0.0)

result = lmfit.minimize(cosine_fit, params, args = (x, y, yerr))

fit_values  = y + result.residual

lmfit.report_errors(params)

x_plot = np.linspace(x.min(),x.max(),1000)

figure = pyplot.figure(1)
figure.clf()

pyplot.plot(x,(b_field-np.average(b_field))*1000,'o')
ax2 = pyplot.twinx()
ax2.plot(x,b_field_freq*1000,'o', markersize = 0.0)
ax2.plot(x_plot,cosine_model(params,x_plot)*1000,linewidth = 3.0)

pyplot.show()
