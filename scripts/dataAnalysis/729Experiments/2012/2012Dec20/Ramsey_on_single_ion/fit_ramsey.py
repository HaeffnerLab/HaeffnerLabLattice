import labrad
import numpy as np
import matplotlib

from matplotlib import pyplot
from scipy.optimize import curve_fit
from scipy.stats import chi2

cxn = labrad.connect()
dv = cxn.data_vault
dv.cd(['','Experiments','729Experiments','RamseyDephase','2012Dec20','2121_24'])
dv.open(1)
data1 = dv.get().asarray

dv.cd(['','Experiments','729Experiments','RamseyDephase','2012Dec20','2123_16'])
dv.open(1)
data2 = dv.get().asarray

data = np.concatenate((data1,data2), axis = 0)

x = data[8:-20,0]
y = data[8:-20,1]
err = np.ones_like(y)

n = len(x) # the number of data points
p0 = [0.5,0,4.22077199e-03] # initial values of parameters
f = lambda x, A, d, freq: A*np.exp(x*d)*(np.cos(2*np.pi*freq*x))+0.5 # define the function to be fitted

p, covm = curve_fit(f, x, y, p0, err) # do the fit
A,d,freq = p
chisq = sum(((f(x,A,d,freq) - y)/err)**2) # compute the chi-squared
ndf = n -len(p) # no. of degrees of freedom
Q = 1. - chi2.cdf(chisq, ndf) # compute the quality of fit parameter Q
chisq = chisq / ndf # compute chi-squared per DOF
A_err,d_err,freq_err = np.sqrt(np.diag(covm)/chisq) # correct the error bars
print A,1/d,freq
#print A_err,d_err,freq_err




figure = pyplot.figure()

pyplot.plot(x,y, 'ko')
x_fit = np.linspace(x.min(), x.max(), 5000)
pyplot.plot(x_fit,f(x_fit,A,d,freq),'r-',linewidth=3.0)
pyplot.show()

#x = np.array([0, 10, 20, 40, 50])
#y = np.array([23, 47, 59, 116, 140])
#err = np.array([1,1,1,1,1])

#n = len(x) # the number of data points
#p0 = [-0.25, 0.2] # initial values of parameters
#f = lambda x, m, b: b + m*x # define the function to be fitted

#p, covm = curve_fit(f, x, y, p0, err) # do the fit
#m,b = p
#chisq = sum(((f(x, m, b) - y)/err)**2) # compute the chi-squared
#ndf = n -len(p) # no. of degrees of freedom
#Q = 1. - chi2.cdf(chisq, ndf) # compute the quality of fit parameter Q
#chisq = chisq / ndf # compute chi-squared per DOF
#merr, berr = np.sqrt(np.diag(covm)/chisq) # correct the error bars
#print m, b
#print merr,berr