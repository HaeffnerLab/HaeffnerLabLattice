import numpy
import labrad
cxn = labrad.connect()
dv = cxn.data_vault
import matplotlib

from matplotlib import pyplot
import scipy
from scipy import optimize
import math



x = 192851; info = ('2012 June 21 delay time 5 ions',  15000, 200, '2012Jun21_{0:=04}_{1:=02}'.format(x/100, x % 100))

name = info[0]
meltingThreshold = info[1]
totalTraces = info[2]
datasetName = info[3]
melted = []
#getting parameters
dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName])
dv.open(1)    
initial_cooling = dv.get_parameter('initial_cooling')
heat_delay = dv.get_parameter('heat_delay')
axial_heat = dv.get_parameter('axial_heat')
readout_delay = dv.get_parameter('readout_delay')
readout_time = dv.get_parameter('readout_time')
#readout range
startReadout =  (axial_heat + initial_cooling + heat_delay + axial_heat + readout_delay ) 
stopReadout = startReadout + readout_time 
#data processing on the fly
dv.cd(['','Experiments','LatentHeat_no729_autocrystal',datasetName,'timetags'])
for dataset in range(1,totalTraces+1):
    #print dataset
    dv.open(int(dataset))
    timetags = dv.get().asarray[:,0]
    countsReadout = numpy.count_nonzero((startReadout <= timetags) * (timetags <= stopReadout))
    countsReadout = countsReadout / float(readout_time) #now in counts/sec
    if countsReadout < meltingThreshold: # melting is less counts
        melted.append(1)
    else:
        melted.append(0)
melted = numpy.array(melted)
meltedPos = numpy.where(melted)
diffs = numpy.ediff1d(meltedPos) - 1

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
    return optimize.leastsq(f, p)


#make figure
figure = pyplot.figure()
figure.clf()
pyplot.suptitle('Melting Distirbution')
binned = numpy.bincount(diffs)#, histtype = 'stepfilled', normed = True)
binned = binned / float(binned.sum())
mean = diffs.mean()
lam = Parameter(mean)
def pois(x): return lam() ** numpy.floor(x) * numpy.exp(-lam()) / scipy.factorial(numpy.floor(x))
sp = numpy.arange(len(binned))
vals = [pois(x) for x in sp]
vals = numpy.array(vals)
vals = vals / vals.sum()
pyplot.plot(sp, vals, drawstyle = 'steps-post', label = 'poisson mean {:.2f}'.format(mean))


pyplot.plot(binned, color = 'black', drawstyle = 'steps-post',label = 'measured')
pyplot.xlabel('Iterations between melts')
pyplot.ylabel('Occurence Prob')
pyplot.legend()
pyplot.show()