import labrad
import numpy as np
from matplotlib import pyplot
import lmfit



def axial_model(params, x):
    A = params['A'].value
    B= params['B'].value
    C = params['C'].value
    output = A*np.abs(x)**B+C
    return output
'''
define how to compare data to the function
'''
def axial_fit(params , x, data, err):
    model = axial_model(params, x)
    return (model - data)/err

#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

#change directory

figure = pyplot.figure(1)
figure.clf()
w_z = np.array([10.0,9.0,8.0,7.0,6.0,5.0,4.0,3.0,2.0,1.0,0.8,0.6,0.4])
freq = np.array([282.9, 271.6, 259.8, 247.3, 234.3, 220.5, 205.7, 189.7, 172.4,153.0,148.8,144.6,140.2])

params = lmfit.Parameters()

x = w_z
y = freq
yerr = freq*0.02

params.add('A', value = 0.4)
params.add('B', value = 1)
params.add('C', value = 1)
result = lmfit.minimize(axial_fit, params, args = (x, y, yerr))

fit_values  = y + result.residual

lmfit.report_errors(params)

x_plot = np.linspace(x.min(),x.max(),1000)

#figure.suptitle('Spectrum 2013Mar13 1623_50, 10ms excitation')
#pyplot.ylabel('Parity signal')
#pyplot.xlabel('Time (us)')
pyplot.plot(x, y, 'o')
pyplot.plot(x_plot,axial_model(params,x_plot))
pyplot.show()
