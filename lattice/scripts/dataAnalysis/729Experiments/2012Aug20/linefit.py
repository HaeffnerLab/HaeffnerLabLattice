import numpy as np
from scipy import optimize
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
#optimization
class Parameter:
    def __init__(self, value):
            self.value = value

    def set(self, value):
            self.value = value

    def __call__(self):
            return self.value
def fit(function, parameters, y, x = None):
    def f(params):
        i = 0
        for p in parameters:
            p.set(params[i])
            i += 1
        return y - function(x)

    if x is None: x = np.arange(y.shape[0])
    p = [param() for param in parameters]
    return optimize.leastsq(f, p)

heating_time = np.array([0, 10, 20, 40, 50])
nbar = np.array([45, 80, 110, 230, 270])

# giving initial parameters
m = Parameter(10)
b = Parameter(50)
# define your function:
def f(x): return m() * x + b()
p,success = fit(f, [m, b], y = nbar, x = heating_time)
print p,success

pyplot.figure()

pyplot.plot(heating_time, nbar, 'bo')
pyplot.plot(heating_time, f(heating_time), '-', label = 'linear fit m = {0:.1f} nbar / ms'.format(m()))
pyplot.legend()
pyplot.ylabel('nbar')
pyplot.xlabel('Time (ms)')
pyplot.show()