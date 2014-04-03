import labrad
import numpy as np
from matplotlib import pyplot

import lmfit

def decay_model(params, x):
    T2 = params['T2'].value
    freq = params['freq'].value
    offset = params['offset'].value
    phase = params['phase'].value
    t = x
    model =  0.5*(1+np.cos(2*np.pi*freq*t+phase))*np.exp(-t/T2)+offset*(1-np.exp(-t/T2))
    return model


def decay_fit(params , x, data, err):
    model = decay_model(params, x)
    return (model - data)/err



#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault


dv.cd(['','Experiments','RamseyScanGap','2014Apr02','1627_09'])
dv.open(1)
data = dv.get().asarray
x = data[:,0]/1000000
y = data[:,1]

x = x[2:]
y = y[2:]

yerr = np.sqrt(y*(1-y)/100)+0.01

##fitter
params = lmfit.Parameters()

params.add('T2', value = 0.000331)
params.add('freq', value = 15344)
params.add('offset', value = 0.334)
params.add('phase', value = -0.893569)

result = lmfit.minimize(decay_fit, params, args = (x, y, yerr))

fit_values  = y + result.residual

lmfit.report_errors(params)

#lmfit.report_fit(params)

#change directory

Gamma = 560e6/(2*np.pi*params['T2'].value*params['freq'].value)/1000000
print Gamma

x_plot = np.linspace(x.min(),x.max(),1000)

figure = pyplot.figure(1)
figure.clf()
pyplot.plot(x,y,'o')
pyplot.plot(x_plot,decay_model(params,x_plot),linewidth = 3.0)

pyplot.show()