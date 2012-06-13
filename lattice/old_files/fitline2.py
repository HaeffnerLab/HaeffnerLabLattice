from scipy import optimize
from numpy import *
from matplotlib import pyplot
from matplotlib import *

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

    if x is None: x = arange(y.shape[0])
    p = [param() for param in parameters]
    return optimize.leastsq(f, p)


# giving initial parameters
m = Parameter(1)
b = Parameter(50)

# define your function:
def f(x): return m() * x + b()

c1 = array([-40.4 , -124.5 ,  -167 , -213])
c2 = array([ 4.4 , -156.8 , -242 , -328])

p,success = fit(f, [m, b], y = c2, x = c1)

pyplot.plot(c1,c2,'b^',c1,f(c1), markersize=10)
pyplot.title("Compensation voltages to compensate when looking from top")
pyplot.xlabel("c1")
pyplot.ylabel("c2")
ax = pyplot.axes()
pyplot.text(0.5, 0.2,'c2 = %.2f*c1 + %.2f'  % (m(),b()), fontsize=12,transform = ax.transAxes)
ax = pyplot.axes()
pyplot.show()
print 