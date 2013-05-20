#plot the binned timetags
from constants import constants as c
import numpy as np
import matplotlib

from matplotlib import pyplot
from scipy.optimize import curve_fit
from scipy.stats import chi2


f = np.load(c.bin_filename)
bins = f[:,0]
hist = f[:,1]
bins = bins*1e6 #plot time bins in microseconds


fit_domain = (55.0, 90.0)
where = np.where((fit_domain[0] <= bins) * (bins <= fit_domain[1]))
x, y = bins[where], hist[where]

err = np.sqrt(y)

n = len(x) # the number of data points
p0 = [1451.0, 61.8, 10000.0 , 62.6, -1.0, 81.0, -10000.0, 82.32] # initial values of parameters

def f(x, background, start_rise ,rise_slope, start_top, top_slope, start_fall, fall_slope, end_fall):
    '''
    function starts at the level of background
    then rises
    then stays hight
    then falls to the level of background
    '''
    y = np.zeros_like(x)
    before_start_where   = (x < start_rise)
    y[before_start_where] = background
    rise_where = (x >= start_rise) * (x <= start_top)
    y[rise_where] = background  + (x[rise_where] - start_rise) * rise_slope
    top_where = (x >= start_top) * (x <= start_fall)
    y[top_where] = background + (start_top - start_rise) * rise_slope + ( x[top_where] - start_top) * top_slope
    fall_where = (x >= start_fall) * (x <= end_fall)
    y[fall_where] =  background + (start_top - start_rise) * rise_slope + ( start_fall - start_top) * top_slope + (x[fall_where] - start_fall) * fall_slope
    after_end_fall = x >= end_fall
    y[after_end_fall] = background 
    return y
    
    

p, covm = curve_fit(f, x, y, p0, err) # do the fit
print p
#m,b = p
#chisq = sum(((f(x, m, b) - y)/err)**2) # compute the chi-squared
#ndf = n -len(p) # no. of degrees of freedom
#Q = 1. - chi2.cdf(chisq, ndf) # compute the quality of fit parameter Q
#chisq = chisq / ndf # compute chi-squared per DOF
#merr, berr = np.sqrt(np.diag(covm)/chisq) # correct the error bars
#print m, b
#print merr,berr
bin_size = bins[1] - bins[0]
#slope_str = u'Linear Fit, m = {0:.1f} \261 {1:.1f} counts per \265s'.format(m, merr, bin_size)
#slope_str += u'\n b = {0:.1f} \261 {1:.1f} counts'.format(b , berr)

pyplot.figure()
pyplot.plot(bins, hist, '.k', markersize=0.7)
pyplot.plot(x, f(x, *p), 'r')
pyplot.xlim(*fit_domain)
pyplot.ylim(ymin = 0, ymax = 15000.0)
pyplot.title('Branching Ratio ' + c.bin_filename)
#pyplot.annotate(slope_str, xy=(0.55, 0.80), xycoords='axes fraction')
pyplot.xlabel(u'Time \265s')
pyplot.ylabel(u'Photons per bin of {} \265s'.format(bin_size))

pyplot.figure()
#plot background subtracted 397 peak
offset = 40.0
pyplot.plot(bins, hist, '.k', markersize=0.9)
pyplot.plot(bins, f(bins + 40.0, *p), 'r')
#subtracted = hist - f(bins, *p)
#pyplot.plot(bins, subtracted, 'b')
pyplot.xlim(fit_domain[0] - offset, fit_domain[1] - offset)
pyplot.show()