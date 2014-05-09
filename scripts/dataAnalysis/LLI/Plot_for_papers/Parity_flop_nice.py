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

plot2 = figure.add_subplot(111)

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

pyplot.plot(x_hot, y_hot,'o',color='#A0A8B8')

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

pyplot.plot(x_plot,cosine_model(params,x_plot),'-',linewidth=1.5,color='#00246B')



#figure.suptitle('Spectrum 2013Mar13 1623_50, 10ms excitation')
#pyplot.ylabel('Parity flop with no cooling')
#pyplot.xlabel('Time (s)')
pyplot.show()
