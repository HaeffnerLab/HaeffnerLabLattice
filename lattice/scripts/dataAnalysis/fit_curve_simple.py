import labrad
import numpy
from scipy import optimize
from scipy.interpolate import interp1d
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
#get access to servers
cxn = labrad.connect()
dv = cxn.data_vault


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
dv.cd(['','Experiments','EnergyTransportv2', '2011Dec07_1610_00'])
dv.open(5)
data = dv.get().asarray
x = data[:,0]
y = data[:,1] / data[:,1].max()
slice = (x >=  0.050) * (x <=  0.250)
x = x[slice]
y = y[slice]


# giving initial parameters
#A = Parameter(200)
#B = Parameter(1)
#exponent = Parameter(200)
#offset = Parameter(1)
#t0 = Parameter(0.10)

## define your function:
#def fitfunc(x): return A() / (B() + numpy.exp(-(-x - t0()))/exponent()) + offset()
#
## fit! (given that data is an array with the data to fit)
#fit(fitfunc, [A, B, exponent, offset, t0], y , x)
#print A(), B(), exponent(), offset(), t0()

ymodel = numpy.array([1., 0.911095, 0.839903, 0.781557, 0.732833, 0.691503, 0.655982, \
0.625109, 0.598015, 0.574034, 0.55265, 0.533456, 0.516124, 0.500391, \
0.48604, 0.472892, 0.460799, 0.449635, 0.439293, 0.429684, 0.42073, \
0.412364, 0.404527, 0.39717, 0.390247, 0.38372, 0.377555, 0.37172, \
0.366189, 0.360937, 0.355942, 0.351186, 0.346651, 0.34232, 0.338179, \
0.334215, 0.330417, 0.326774, 0.323275, 0.319911, 0.316675, 0.313559, \
0.310555, 0.307658, 0.304861, 0.302158, 0.299545, 0.297016, 0.294568, \
0.292196, 0.289896, 0.287665, 0.2855, 0.283397, 0.281353, 0.279366, \
0.277433, 0.275552, 0.27372, 0.271935, 0.270195, 0.268499, 0.266845, \
0.26523, 0.263653, 0.262114, 0.260609, 0.259139, 0.257701, 0.256295, \
0.254919, 0.253572, 0.252254, 0.250962, 0.249697, 0.248458, 0.247242, \
0.246051, 0.244882, 0.243735, 0.24261, 0.241505, 0.240421, 0.239356, \
0.23831, 0.237282, 0.236272, 0.235279, 0.234303, 0.233344, 0.232399, \
0.231471, 0.230557, 0.229658, 0.228772, 0.227901, 0.227043, 0.226197, 
 0.225365, 0.224545, 0.223736])

xmodel = numpy.arange(ymodel.size)
xscale = 1/465.0
xoffset= 0.07
xmodel = xscale * xmodel + xoffset
background = 0.22
ymodel = (ymodel + background) / (1 + background)

figure = pyplot.figure()
figure.clf()
pyplot.plot(x, y)
pyplot.plot(xmodel, ymodel)
#figure.suptitle('QuickMeasurements, Power Monitoring 3')
pyplot.xlabel('Time (sec)')
pyplot.ylabel('Fluorescence, Arb')
pyplot.show()
