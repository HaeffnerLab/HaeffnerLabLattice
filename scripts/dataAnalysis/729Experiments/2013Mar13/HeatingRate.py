import labrad
import matplotlib

from matplotlib import pyplot, pylab
import numpy as np
from scipy import optimize
from labrad import units as U

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

waiting_times = [0,60,200,1000,5000,10000]
nbar_without_dephasing = [0.104341219659,0.132849600291,0.169919673967,0.200537464564,0.76912820992,1.41854604183]
nbar_with_dephasing = [0.104341219659,0.132857576981,0.144248929096,0.203999231286,0.606425354475,1.0227408143]

waiting_times = np.array(waiting_times)
nbar_without_dephasing = np.array(nbar_without_dephasing)
nbar_with_dephasing = np.array(nbar_with_dephasing)

a = Parameter(100.0)
b = Parameter(0.0)

def f(x):
    return a() * x + b() 

print 'Fitting...'
p,success = fit(f, [a,b], y = nbar_without_dephasing, x = waiting_times)
print 'Fitting DONE.'
print 1000*b(),' phonons/us' 

pyplot.plot(waiting_times,nbar_without_dephasing, 'ro',label='without dephasing')
pyplot.plot(waiting_times,f(waiting_times), 'r-',label='fit with {:.2f} phonons/ms'.format(1000*b()))
pyplot.xlim((0,10000))
pyplot.ylim((0,1.5))

print 'Fitting...'
p,success = fit(f, [a,b], y = nbar_with_dephasing, x = waiting_times)
print 'Fitting DONE.'
print 1000*b(),' phonons/ms' 

pyplot.plot(waiting_times,nbar_with_dephasing, 'bs',label='with dephasing')
pyplot.plot(waiting_times,f(waiting_times), 'b-',label='fit with {:.2f} phonons/ms'.format(1000*b()))
pyplot.xlabel('t in us')
pyplot.ylim((0,1.5))
pyplot.ylabel('nbar')
pyplot.legend(loc=4)
pyplot.title('Heating rates with and without dephasing')
pyplot.show()
