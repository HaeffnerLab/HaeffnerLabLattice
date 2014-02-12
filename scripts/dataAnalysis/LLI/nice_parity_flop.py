import labrad
import numpy as np
from matplotlib import pyplot
import lmfit


def cosine_model(params, x):
    A = params['A'].value
    tau= params['tau'].value
    freq = params['freq'].value
    phase=params['phase'].value
    output = A*np.cos(2.0*np.pi*x*freq+phase)*np.exp(-x/tau)
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

#change directory

figure = pyplot.figure(1)
figure.clf()
plot1 = figure.add_subplot(211)


#dv.cd(['','Experiments','Ramsey2ions_ScanGapParity','2014Jan29','1756_34'])
dv.cd(['','Experiments','Ramsey2ions_ScanGapParity','2014Feb10','1854_26'])
dv.open(1)
data = dv.get().asarray
x1 = data[:,0]
y1 = data[:,2]
yy1 = data[:,3]

dv.cd(['','Experiments','Ramsey2ions_ScanGapParity','2014Feb10','1858_08'])
dv.open(1)
data = dv.get().asarray
x2 = data[:,0]
y2 = data[:,2]
yy2 = data[:,3]

x_cooled = np.concatenate((x1,x2),axis=0)/1000000
y_cooled = np.concatenate((y1,y2),axis=0)
yy_cooled = np.concatenate((yy1,yy2),axis=0)

pyplot.plot(x_cooled, y_cooled,'o-')
pyplot.plot(x_cooled, yy_cooled,'o-')

pyplot.axis([0,0.2,0.0,1.0])

pyplot.ylabel('Individual ion excitation')

plot2 = figure.add_subplot(212)

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

pyplot.plot(x_cooled, y_cooled,'or')

pyplot.axis([0,0.2,-0.6,0.6])

pyplot.ylabel('Parity oscillations')

yerr = np.ones_like(y_cooled)*0.1

#yerr = np.absolute(y_cooled)*0.1+0.1

print yerr

params = lmfit.Parameters()

params.add('A', value = 0.4)
params.add('tau', value = 1)
params.add('freq', value = 55.3)
params.add('phase', value = 0.0)

result = lmfit.minimize(cosine_fit, params, args = (x_cooled, y_cooled, yerr))

#print np.average(result.residual**2)/np.size(x_cooled)

red_chi = np.sum(result.residual**2)/(np.size(y_cooled)-4)

print red_chi

fit_values  = y_cooled + result.residual

lmfit.report_errors(params)

x_plot = np.linspace(x_cooled.min(),x_cooled.max(),1000)

pyplot.plot(x_plot,cosine_model(params,x_plot),linewidth=3)

#figure.suptitle('Spectrum 2013Mar13 1623_50, 10ms excitation')
pyplot.xlabel('Time (s)')
pyplot.show()
