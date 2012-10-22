#
# Python program written by Matt Wittmann
#
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import chi2

x = np.array([0, 10, 20, 40, 50])
y = np.array([23, 47, 59, 116, 140])
err = np.array([1,1,1,1,1])

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