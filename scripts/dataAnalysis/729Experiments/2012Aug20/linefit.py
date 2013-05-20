import numpy as np
from scipy import optimize
import matplotlib

from matplotlib import pyplot

fig_title = '2012Aug20: first measurements'
heating_time = np.array([0, 10, 20, 40, 50])
nbar = np.array([23, 47, 59, 116, 140])
# define your function:
def f(x, m ,b): return m * x + b
# giving initial parameters
init_guess = [2, 50] #m, b
#minimize initially assuming same error for each point 
out = optimize.curve_fit(f, heating_time, nbar, p0=init_guess, sigma=None, full_output = True)
m,b = out[0]
print 'init fit', m, b
estimated_sigma_sq = sum((f(heating_time, m ,b) -  nbar)**2 / (len(nbar) - 2)) #estiamte sigma^2 - the uncertainy of the y value of the points
#see 'a practical guide to data analysis ... (2.19)
estimated_sigma = np.sqrt(estimated_sigma_sq)
print 'estimated sigma', estimated_sigma
sigma_b_pr =  estimated_sigma / np.sqrt(len(nbar))
x_avg = np.average(heating_time)
sigma_m =  estimated_sigma / np.sqrt( np.sum ((heating_time - x_avg)**2))
sigma_b = np.sqrt(sigma_m**2 * x_avg**2 + sigma_b_pr**2)
print sigma_b , sigma_m
print sigma_b / sigma_m

##pyplot.figure()
#pyplot.title(fig_title)
#pyplot.plot(heating_time, nbar, 'bo')
#pyplot.plot(heating_time, f(heating_time), '-', label = 'linear fit m = {0:.1f} nbar / ms'.format(m()))
#pyplot.legend()
#pyplot.ylabel('nbar')
#pyplot.xlabel('Time (ms)')
#pyplot.show()