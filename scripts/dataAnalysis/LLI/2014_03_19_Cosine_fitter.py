import labrad
import numpy as np
from matplotlib import pyplot

import lmfit

def cosine_model(params, x):
    A = params['A'].value
    tau= params['tau'].value
    freq = params['freq'].value
    phase=params['phase'].value
    offset=params['offset'].value
    output = A*np.cos(2*np.pi*x*freq+phase)*np.exp(-x/tau)+offset
    return output
'''
define how to compare data to the function
'''
def cosine_fit(params , x, data, err):
    model = cosine_model(params, x)
    return (model - data)/err

#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault


dv.cd(['','Experiments','Parity_LLI_scan_gap','2014Mar30','1722_00'])
dv.open(2)
data = dv.get().asarray
x = data[:,0]/1000000
y = data[:,1]
yerr = np.sqrt(1-y**2)/20.0

##fitter
params = lmfit.Parameters()

params.add('A', value = -0.5)
params.add('tau', value = 1)
params.add('freq', value = 370)
params.add('phase', value = 0.0)
params.add('offset', value = 0.0)

result = lmfit.minimize(cosine_fit, params, args = (x, y, yerr))

fit_values  = y + result.residual

lmfit.report_errors(params)

#lmfit.report_fit(params)

#change directory
x_plot = np.linspace(x.min(),x.max(),1000)

figure = pyplot.figure(1)
figure.clf()
pyplot.plot(x,y,'o')
pyplot.plot(x_plot,cosine_model(params,x_plot),linewidth = 3.0)

pyplot.show()
