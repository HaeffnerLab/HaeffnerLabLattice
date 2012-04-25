import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
import numpy as np

def makePlot(bins,binned):
    bins = bins * 10.0**6 #now in microseconds
    pyplot.figure()
    pyplot.plot(bins[0:-1],binned)
    pyplot.show()

if __name__ == '__main__':
    fileName = '2012Apr24_1625_39binning.npz'
    f = np.load(fileName)
    binned = f['binned']
    bins = f['bins']
    makePlot(bins, binned)