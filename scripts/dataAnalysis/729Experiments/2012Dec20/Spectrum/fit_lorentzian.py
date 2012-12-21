import labrad
import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
from scipy.optimize import curve_fit
from scipy.stats import chi2

#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault

#change directory

figure = pyplot.figure()
dv.cd(['','Experiments','729Experiments','Spectrum','2012Dec20','2158_40'])
dv.open(1)
data = dv.get().asarray
x = (data[:,0]-226.589)*1000*2
y = data[:,1]
err = np.ones_like(y)*0.05

n = len(x) # the number of data points
p0 = [0, 3,0.5] # initial values of parameters
f = lambda x, x_0, b, a: a*b*(1/(2*np.pi))/((b/2)**2+(x-x_0)**2) # define the function to be fitted

p, covm = curve_fit(f, x, y, p0, err) # do the fit
x_0,b,a = p
chisq = sum(((f(x, x_0,b,a) - y)/err)**2) # compute the chi-squared
ndf = n -len(p) # no. of degrees of freedom
Q = 1. - chi2.cdf(chisq, ndf) # compute the quality of fit parameter Q
chisq = chisq / ndf # compute chi-squared per DOF
x_0_err,b_err,a_err = np.sqrt(np.diag(covm)/chisq) # correct the error bars
print x_0,b,a
print x_0_err,b_err,a_err
print chisq


x = x-x_0
pyplot.plot(x,y, 'ko')
x_fit = np.linspace(x.min(), 4*x.max(), 5000)
pyplot.plot(x_fit-x_0,f(x_fit,x_0,b,a),'r-',linewidth=3.0)

pyplot.annotate('FWHM = {0:.3f} kHz'.format(b), xy=(0.60, 0.8), xycoords='axes fraction',fontsize=15)

pyplot.xlabel( 'Frequency (kHz)',fontsize=15)
pyplot.ylabel('Excitation probability',fontsize=15)
#pyplot.title('Excitation spectrum of 729 nm transition',fontsize=20)
pyplot.ylim([0,1.0])
pyplot.xlim([-1.5,1.5])
pyplot.show()
