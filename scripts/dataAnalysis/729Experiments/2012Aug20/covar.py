import numpy as np
from scipy import optimize
import matplotlib

from matplotlib import pyplot

fig_title = '2012Aug20: first measurements, trap_freq ~ 1MHz'
heating_time = np.array([0, 25, 50, 100])
nbar = np.array([28, 59, 59, 102])
# define your function:
def f(x, m ,b): return m * x + b
# giving initial parameters
init_guess = [2, 50] #m, b
#minimize initially assuming same error for each point 
out = optimize.curve_fit(f, heating_time, nbar, p0=init_guess, sigma=None, full_output = True)
fit_params, covar, kwarg, messages, success =  out
m,b = fit_params
print 'completed fit in {} calls'.format(kwarg['nfev'])
print 'Fit Parameters m = {0:.2f}, b = {1:.2f}'.format( m, b)

sigma_effective = np.sqrt( sum((f(heating_time, m, b) - nbar)**2) / (len(nbar) - 2.) )
#the covariant matrix is computed such that the square root of diagonal gives the uncertainties
#MORE DETAIL: if we made sigma = [1,1..,1] or [10,10...,10] in curve_fit, this covariant DOES NOT change because the sigma array are only used as relative weights.
#to account for this lack of overall scaling, curve_fit computes sigma_effective: the uncertainy in the measurement most consistent with the fit, "assuming normality"
#and then uses it as a prefactor with covar to make this work
#http://comments.gmane.org/gmane.comp.python.scientific.user/29982
m_err = np.sqrt(covar[0][0])
b_err = np.sqrt(covar[1][1])


pyplot.figure()
pyplot.title(fig_title)
label = 'linear fit\nm = {0:.2f} +/- {1:.2f} nbar / ms \n'.format(m, m_err)
label += 'b = {0:.2f} +/- {1:.2f} nbar'.format(b, b_err)
pyplot.plot(heating_time, f(heating_time, m, b), '-', label = label)
pyplot.errorbar(heating_time, nbar, yerr=sigma_effective, fmt='bo')
pyplot.legend()
pyplot.ylabel('nbar')
pyplot.xlabel('Time (ms)')
pyplot.show()