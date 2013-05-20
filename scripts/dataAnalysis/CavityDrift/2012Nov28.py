import labrad
from matplotlib import pyplot
import numpy as np
from scipy.optimize import curve_fit

#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

directory = ['','Drift_Tracking','Cavity729','2012Nov28']
filename = '00007 - Cavity Drift 2012Nov28_1758_57'
#change directory

figure = pyplot.figure()

dv.cd(directory)
dv.open(filename)
data = dv.get().asarray
x_axis = data[:,0]

x_axis = x_axis[2:] / 60.0
x_axis = x_axis - x_axis.min()

y_axis = data[:,1][2:] * 1000.0
y_axis = 2 * y_axis #doubline for double pass
ymin = y_axis.min()
y_axis = y_axis - ymin

#fit to a line

p0 = [-0.25, 0.2] # initial values of parameters
f = lambda x, m, b: b + m*x # define the function to be fitted

p, covm = curve_fit(f, x_axis, y_axis, p0) # do the fit
m,b = p


pyplot.plot(x_axis,y_axis, 'k*')
pyplot.plot(x_axis, f(x_axis, m, b), 'r', label = 'Slope of {0:.1f} KHz / min'.format(abs(m)))
pyplot.xlabel( 'Time (min)')
pyplot.ylabel('Frequency kHz + 2 * {0:.0f} kHz'.format(ymin/2.0))
pyplot.legend()
pyplot.title(filename)
pyplot.show()
