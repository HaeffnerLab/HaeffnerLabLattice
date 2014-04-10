import labrad
import numpy as np
from matplotlib import pyplot
import lmfit

def power_model(params, x):
    pi_time = params['pi_time'].value
    conversion = params['conversion'].value
    T = params['T2']
    power_data = 10**(x/10)
    rabi_freq = power_data/conversion
    excitation = (np.sin(rabi_freq*pi_time))**2*np.exp(-T*rabi_freq)
    return excitation

def micro_fit(params , x, data, err):
    model = power_model(params, x)
    return (model - data)/err

cxn = labrad.connect()
dv = cxn.data_vault

dv.cd(['','Experiments','Rabi_power_flopping_2ions','2014Mar16','1209_14'])
dv.open(1)
data = dv.get().asarray
x = data[:,0]
y = data[:,1]
x = x[:-10]
y = y[:-10]
yerr = 0.02

figure = pyplot.figure(1)
figure.clf()


params = lmfit.Parameters()
params.add('pi_time', value = 50e-6, vary = False)
params.add('conversion', value = 0.55e-6)
params.add('T2', value = 0.0, vary= False)

result = lmfit.minimize(micro_fit, params, args = (x, y,yerr))

fit_values  = y + result.residual

#lmfit.report_errors(params)

lmfit.report_fit(params)
print params['conversion']*1e6

pyplot.plot(x,y,'o')
pyplot.plot(x,power_model(params,x))

#pyplot.figure()
#pyplot.plot(10**(x/10), y)

pyplot.show()

