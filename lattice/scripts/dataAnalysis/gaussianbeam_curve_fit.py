import labrad
import numpy
from scipy import optimize
from scipy.interpolate import interp1d
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
import math



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

    if x is None: x = numpy.arange(y.shape[0])
    p = [param() for param in parameters]
    optimize.leastsq(f, p)
#change directory and loading
x = numpy.array([121500, 144500, 175500, 209000, 233000, 258000]) # distance from beam
y = numpy.array([563.036, 746.661, 840.238, 1068.48, 1175.19, 1557.14])
g = numpy.array([(23.25 + 4.05 - 2.5)*10000, (12.7 + 23.25 + 4.05 - 2.5)*10000])
h = numpy.array([1008.078, 1340.84])


#x = numpy.array(x)
#y = numpy.array(y)

# giving initial parameters
lam = .4092

w0 = Parameter(25)
#A = Parameter(200)
#B = Parameter(1)
#exponent = Parameter(200)
#offset = Parameter(1)
#t0 = Parameter(0.10)

## define your function:
def fitfunc(x): return w0()*numpy.sqrt(1 + ((x)*lam/(numpy.pi*w0()**2))**2)
#
## fit! (given that data is an array with the data to fit)
fit(fitfunc, [w0, ], y , x)
print w0()

xmodel = numpy.arange(300000)
ymodel = w0()*numpy.sqrt(1 + ((xmodel)*lam/(numpy.pi*w0()**2))**2)

figure = pyplot.figure()
figure.clf()
pyplot.plot(x, y, 'rs')
pyplot.plot(xmodel, ymodel)

fit(fitfunc, [w0, ], h , g)
print w0()

xmodel = numpy.arange(300000)
ymodel = w0()*numpy.sqrt(1 + ((xmodel)*lam/(numpy.pi*w0()**2))**2)

pyplot.plot(g, h, 'bs')
pyplot.plot(xmodel, ymodel)
pyplot.xlabel('Distance to Center of Cavity (microns)')
pyplot.ylabel('Waist (microns)')
#figure.suptitle('QuickMeasurements, Power Monitoring 3')
pyplot.show()
