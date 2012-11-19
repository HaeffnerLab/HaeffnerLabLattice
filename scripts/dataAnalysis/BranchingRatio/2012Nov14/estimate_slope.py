#plot the binned timetags
from constants import constants as c
import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
from scipy.optimize import curve_fit
from scipy.stats import chi2


f = np.load(c.bin_filename)
bins = f[:,0]
hist = f[:,1]
bins = bins*1e6 #plot time bins in microseconds


fit_domain = (63.0, 81.0)
where = np.where((fit_domain[0] <= bins) * (bins <= fit_domain[1]))
x, y = bins[where], hist[where]

err = np.sqrt(y)

n = len(x) # the number of data points
p0 = [-0.25, 0.2] # initial values of parameters
f = lambda x, m, b: b + m*x # define the function to be fitted

p, covm = curve_fit(f, x, y, p0, err) # do the fit
m,b = p
chisq = sum(((f(x, m, b) - y)/err)**2) # compute the chi-squared
ndf = n -len(p) # no. of degrees of freedom
Q = 1. - chi2.cdf(chisq, ndf) # compute the quality of fit parameter Q
chisq = chisq / ndf # compute chi-squared per DOF
merr, berr = np.sqrt(np.diag(covm)/chisq) # correct the error bars
print m, b
print merr,berr
bin_size = bins[1] - bins[0]
slope_str = u'Linear Fit, m = {0:.1f} \261 {1:.1f} counts per \265s'.format(m, merr, bin_size)
slope_str += u'\n b = {0:.1f} \261 {1:.1f} counts'.format(b , berr)

pyplot.plot(bins, hist, '.k', markersize=0.7)
pyplot.plot(x, f(x, m, b), 'r')
pyplot.xlim(xmin = 60.0, xmax = 83.0)
pyplot.ylim(ymax = 15000.0)
pyplot.title('Branching Ratio ' + c.bin_filename)
pyplot.annotate(slope_str, xy=(0.55, 0.80), xycoords='axes fraction')
pyplot.xlabel(u'Time \265s')
pyplot.ylabel(u'Photons per bin of {} \265s'.format(bin_size))
pyplot.show()