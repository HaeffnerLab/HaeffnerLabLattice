import labrad
from matplotlib import pyplot
import numpy as np
from scipy.optimize import curve_fit

#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

directory = ['','Drift_Tracking','Cavity729','2013May24']
filename = '00001 - Cavity Drift 2013May24_1106_25'
#change directory

figure = pyplot.figure()

dv.cd(directory)
dv.open(filename)
data = dv.get().asarray

x_axis = data[1::,0]/60
y_axis = (data[1::,2]-data[1,2])*1000 #in miligauss

p0 = [-0.25, 0.2] # initial values of parameters
f = lambda x, m, b: b + m*x # define the function to be fitted

p, covm = curve_fit(f, x_axis, y_axis, p0) # do the fit
m,b = p

pyplot.plot(x_axis,y_axis, 'k*')
pyplot.plot(x_axis, f(x_axis, m, b), 'r', label = '{0:.1f} '.format(abs(m*1000))+r'$\mu$'+'gauss / min',linewidth=3.0)
pyplot.tick_params(axis='both', which='major', labelsize=20)
pyplot.legend()
pyplot.show()
