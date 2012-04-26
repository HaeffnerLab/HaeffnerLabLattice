import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
import numpy as np

def makePlot(dopplerBins,dopplerBinned, bins, binned):
    pyplot.figure()
    ax = pyplot.subplot(121) 
    pyplot.plot(dopplerBins[0:-1],dopplerBinned)
    pyplot.title('Doppler Cooling')
    pyplot.xlabel('Sec')
    pyplot.ylabel('Counts/Sec')
    pyplot.subplot(122, sharey = ax) 
    pyplot.title('Experimental Cycle')
    pyplot.plot(bins[0:-1],binned)
    ax = pyplot.gca()
    ax.ticklabel_format(style = 'sci', scilimits = (0,0), axis = 'x')
    pyplot.xlabel('Sec')
    pyplot.ylabel('Counts/Sec')
    pyplot.show()

if __name__ == '__main__':
    fileName = '2012Apr24_1625_39binning.npz'
    f = np.load(fileName)
    binned = f['binned']
    bins = f['bins']
    dopplerBins = f['dopplerBins']
    dopplerBinned = f['dopplerBinned']
    makePlot(dopplerBins, dopplerBinned, bins, binned)
    