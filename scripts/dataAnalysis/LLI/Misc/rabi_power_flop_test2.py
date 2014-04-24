import labrad
import numpy as np
from matplotlib import pyplot
import lmfit

def power_model(params, x):
    target_power = params['target_power'].value
    conversion = (2*10**(target_power/10))/np.pi
    power_data = 10**(x/10)
    rabi_freq = power_data/conversion
    excitation = (np.sin(rabi_freq))**2
    return excitation

def micro_fit(params , x, data, err):
    model = power_model(params, x)
    return (model - data)/err

cxn = labrad.connect()
dv = cxn.data_vault

dv.cd(['','Experiments','Rabi_power_flopping_2ions','2014Mar16','1216_19'])
dv.open(1)
data = dv.get().asarray
x = data[:,0]
y = data[:,1]
x = x[:-16]
y = y[:-16]
yerr = 0.02

### starting guess ####
initial_target_power_guess = x[np.argmax(y)]

figure = pyplot.figure(1)
figure.clf()


params = lmfit.Parameters()
params.add('target_power', value = initial_target_power_guess)

result = lmfit.minimize(micro_fit, params, args = (x, y,yerr))

fit_values  = y + result.residual


lmfit.report_fit(params)

x_sample = np.linspace(10**(x[0]/10),10**(x[-1]/10),40)

pyplot.plot(10**(x/10),y,'o')
#pyplot.plot(10**(x/10),power_model(params,x))
pyplot.plot(x_sample,power_model(params,10*np.log10(x_sample)),'-')



pyplot.show()

