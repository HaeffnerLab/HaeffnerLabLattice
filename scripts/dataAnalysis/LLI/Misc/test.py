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
    output = A*np.cos(2.0*np.pi*x*freq+phase)*np.exp(-x/tau)+offset
    return output
'''
define how to compare data to the function
'''
def cosine_fit(params , x, data,err):
    model = cosine_model(params, x)
    return (model - data)/err

cxn = labrad.connect()
dv = cxn.data_vault

#change directory

figure = pyplot.figure(1)
figure.clf()


#dv.cd(['','Experiments','Ramsey2ions_ScanGapParity','2014Jan29','1756_34'])
dv.cd(['','Experiments','Ramsey2ions_ScanGapParity','2014Feb10','1854_26'])
dv.open(2)
data = dv.get().asarray
x1 = data[:,0]
y1 = data[:,1]

dv.cd(['','Experiments','Ramsey2ions_ScanGapParity','2014Feb10','1858_08'])
dv.open(2)
data = dv.get().asarray
x2 = data[:,0]
y2 = data[:,1]

x_cooled = np.concatenate((x1,x2),axis=0)/1000000
y_cooled = np.concatenate((y1,y2),axis=0)

#x_cooled = x1/1000000
#y_cooled = y1

#pyplot.plot(x_cooled, y_cooled,'ob')

pyplot.axis([0,0.2,-0.6,0.6])

pyplot.ylabel('Parity flop with cooling')

yerr = np.sqrt(1-y_cooled**2)/20

params = lmfit.Parameters()

params.add('A', value = 0.4)
params.add('tau', value = 1)
params.add('freq', value = 55)
params.add('phase', value = 0.0)
params.add('offset', value = 0.0)

result = lmfit.minimize(cosine_fit, params, args = (x_cooled, y_cooled,yerr))

fit_values  = y_cooled + result.residual

lmfit.report_errors(params)

print result.redchi

print params['freq'].stderr

x_plot = np.linspace(x_cooled.min(),x_cooled.max(),1000)

pyplot.errorbar(x_cooled, y_cooled, yerr)

pyplot.plot(x_plot,cosine_model(params,x_plot))

pyplot.xlabel('Time (us)')
pyplot.show()
