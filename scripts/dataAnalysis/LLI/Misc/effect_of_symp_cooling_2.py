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

pyplot.plot(x_cooled, y_cooled,'ob')

pyplot.axis([0,0.2,-0.6,0.6])

pyplot.ylabel('Parity flop with cooling')

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

pyplot.plot(x_plot,cosine_model(params,x_plot),'-b',linewidth=2)



plot2 = figure.add_subplot(212)

#plot parity
#dv.cd(['','Experiments','Ramsey2ions_ScanGapParity','2014Jan29','1756_34'])
dv.cd(['','Experiments','Ramsey2ions_ScanGapParity','2014Feb10','1745_19'])
dv.open(2)
data = dv.get().asarray
x3 = data[:,0]
y3 = data[:,1]


dv.cd(['','Experiments','Ramsey2ions_ScanGapParity','2014Feb10','1752_00'])
dv.open(2)
data = dv.get().asarray
x4 = data[:,0]
y4 = data[:,1]

x_hot = np.concatenate((x3,x4),axis=0)/1000000
y_hot = np.concatenate((y3,y4),axis=0)

pyplot.plot(x_hot, y_hot,'or')

pyplot.axis([0,0.2,-0.6,0.6])

yerr = 0.01

params = lmfit.Parameters()

params.add('A', value = 0.4)
params.add('tau', value = 1)
params.add('freq', value = 50)
params.add('phase', value = 0.0)

result = lmfit.minimize(cosine_fit, params, args = (x_hot, y_hot, yerr))

fit_values  = y_hot + result.residual

lmfit.report_errors(params)

x_plot = np.linspace(x_hot.min(),x_hot.max(),1000)

pyplot.plot(x_plot,cosine_model(params,x_plot),'-r',linewidth=2)



#figure.suptitle('Spectrum 2013Mar13 1623_50, 10ms excitation')
pyplot.ylabel('Parity flop with no cooling')
pyplot.xlabel('Time (s)')
pyplot.show()
