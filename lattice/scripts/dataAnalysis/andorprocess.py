import numpy as np
from scipy import optimize
from scipy.interpolate import interp1d
import matplotlib
matplotlib.use('Qt4Agg')
from pylab import *
from matplotlib import pyplot

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

    if x is None: 
        x = np.arange(y.shape[0])
        p = [param() for param in parameters]
        optimize.leastsq(f, p)
   
rawdata = np.loadtxt('/home/lattice/Downloads/andorimages/andorprocess/s14.asc')
rows, cols = rawdata.shape

# calculate standard deviation
radialData = np.sum(rawdata, 0)/4000
meanRadialData = np.mean(radialData)
sum = 0
for i in range(cols):
    sum = sum + (radialData[i] - meanRadialData)**2
width_x = np.sqrt(sum/meanRadialData)
print 'sum: ', sum
print 'mean: ', meanRadialData
print 'widthx: ', width_x

sigma = Parameter(width_x)
height = Parameter(radialData.max())

def fitfunc(x): return (height()/(sigma()*np.sqrt(2*np.pi)))*exp(-(((meanRadialData-x)/sigma())**2)/2)

fit(fitfunc, [sigma, height, ], radialData , range(cols))
print sigma(), height()


#col = data[:, int(y)]
#width_x = sqrt(abs((range(cols)-x)**2*col).sum()/col.sum())

#procdata = rawdata[:, meanRadialData-width_x:meanRadialData+width_x]
#procdata = rawdata[:, meanRadialData-sigma():meanRadialData+sigma()]
procdata = rawdata[:, 28-5:28+5]

xvalues = range(cols)
data = np.array(rows)
data = np.sum(procdata, 1)
#data = rawdata[:,27]   

pyplot.figure(1)
pyplot.plot(xvalues, (height()/(sigma()*np.sqrt(2*np.pi)))*exp(-(((meanRadialData-xvalues)/sigma())**2)/2))
pyplot.plot(range(cols), radialData)

pyplot.figure(2)
pyplot.plot(range(rows), data)

matshow(rawdata)



show()