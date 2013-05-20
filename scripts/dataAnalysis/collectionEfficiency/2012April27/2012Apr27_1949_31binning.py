import numpy as np
import matplotlib

from matplotlib import pyplot
from scipy import optimize

cycles = 250
repeatitions = 5000
dataset = ('397: -12dBm 866: 0 deg', '2012Apr27_1949_31binning.npz')

class Parameter:
    def __init__(self, value):
            self.value = value

    def set(self, value):
            self.value = value

    def __call__(self):
            return self.value
        
background = Parameter(500)
background397 = Parameter(1000)
A397 = Parameter(12000)
T397 = Parameter(1.0)
on397 = 0.85
on866 = 30.76
background866 = Parameter(500)
A866 = Parameter(1000)
T866 = Parameter(1.0)



def fit(function, parameters, y, x = None):
    def f(params):
        i = 0
        for p in parameters:
            p.set(params[i])
            i += 1
        return y - function(x)

    if x is None: x = np.arange(y.shape[0])
    p = [param() for param in parameters]
    optimize.leastsq(f, p)

def model397(t):
    beforeStart = t <= on397
    ans = background() + background397() + A397()*np.exp(-(t -on397)  / T397())
    ans[beforeStart] = background()
    return ans

def model866(t):
    beforeStart = t <= on866
    ans = background866() + A866()*np.exp(-(t -on866)  / T866())
    ans[beforeStart] = background866()
    return ans

def branching(Ablue, Ared):
    '''given the two areas returns the branching ratio'''
    br = Ared / (Ablue + Ared)
    return br

#pyplot.figure()
label,name = dataset
f = np.load(name)
bins = f['bins']
binned = f['binned']
bins = bins*10.0**6 #now in seconds 

fit(model397,  [background, background397, A397, T397], binned[0:500], bins[0:500])
fit(model866,  [background866, A866, T866], binned[600:], bins[600:-1])


pyplot.plot(bins[:-1],binned, label = label)

print 'fit parameters'
print 'backgruond', background()
print 'background397', background397()
print 'amplitude 397',  A397()
print 'time constant 397', T397()
area397 = A397() * T397()
print '397 area', area397

pyplot.plot(bins[0:500],model397(bins[0:500]), label = 'fit397')
pyplot.plot(bins[600:-1],model866(bins[600:-1]), label = 'fit866')
area866 = A866() * T866()
print '866 area', area866
br = branching(area397, area866)
collectEff = area866 / float(cycles * repeatitions)
print 'branching', br
print 'detecting efficiency', collectEff
ax = pyplot.gca()
ax.ticklabel_format(style = 'sci', scilimits = (0,0), axis = 'x')
pyplot.title(name)
pyplot.xlabel('Micro Sec')
pyplot.ylabel('Counts/Sec')
pyplot.ylim((0,12000))
pyplot.legend()
text = 'Collection Efficiency: {0:.1E}\nBranching Ratio {1:.3f}'
pyplot.text(50,10000,text.format(collectEff,br), horizontalalignment='left')
pyplot.show()