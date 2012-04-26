import numpy as np
import labrad
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

class dataProcessor():
    
    def __init__(self, params):
        self.repumpD = params['repumpD']
        self.repumpDelay = params['repumpDelay']
        self.exciteP = params['exciteP']
        self.finalDelay = params['finalDelay']
        self.dopplerCooling = params['dopplerCooling']
    
    def makePlot(self, dopplerBins,dopplerBinned, bins, binned):
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
        
    def sliceArr(self, arr, start, duration, cyclenumber = 1, cycleduration = 0 ):
        '''Takes a np array arr, and returns a new array that consists of all elements between start and start + duration modulo the start time
        If cyclenumber and cycleduration are provided, the array will consist of additional slices taken between start and 
        start + duration each offset by a cycleduration. The additional elements will added modulo the start time of their respective cycle'''
        starts = [start + i*cycleduration for i in range(cyclenumber)]
        criterion = reduce(np.logical_or, [(start <= arr) & (arr <=  start + duration) for start in starts])
        result = arr[criterion]
        if cycleduration == 0:
            if start != 0:
                result = np.mod(result, start)
        else:
            result = np.mod(result - start, cycleduration)
        return result

if __name__ == '__main__':
    #dataset = '2012Apr24_1702_39'
    #dataset = '2012Apr24_1625_39'
    dataset = '2012Apr24_1629_24'
    experiment = 'collectionEfficiency'
    
    dp = dataProcessor()
    cxn = labrad.connect()
    dv = cxn.data_vault
    

    
    binTime = 40.0*10**-9 #fpga resolution
    cycleTime = repumpD + repumpDelay + exciteP + finalDelay
    binNumber = int(cycleTime / binTime)
    bins = binTime * np.arange(binNumber + 1)
    binned = np.zeros(binNumber)
    
    dopplerBinTime = 1.0*10**-3
    dopplerBinNumber = int(dopplerCooling / dopplerBinTime)
    dopplerBins = dopplerBinTime * np.arange(dopplerBinNumber + 1)
    dopplerBinned = np.zeros(dopplerBinNumber)
    
    dv.cd(['', 'Experiments', experiment, dataset, 'timetags'])
    repeations = len(dv.dir()[1])
    
    import time
    for i in range(1, repeations + 1):
        print 'opening', i
        time.sleep(.1)
        dv.open(i)
        timetags = dv.get().asarray
        sliced = dp.sliceArr(timetags, start = dopplerCooling + iterDelay, duration = cycleTime, cyclenumber = iterationsCycle,  cycleduration = cycleTime)
        binned += np.histogram(sliced,  bins)[0]
        doppler = dp.sliceArr(timetags, start = 0, duration = dopplerCooling + iterDelay)
        dopplerBinned += np.histogram(doppler, dopplerBins)[0]
    
    binned = binned / binTime
    binned = binned / (repeations * iterationsCycle)
    dopplerBinned = dopplerBinned / repeations
    dopplerBinned = dopplerBinned / dopplerBinTime
    
    np.savez('{}binning'.format(dataset), binned = binned, bins = bins, dopplerBins = dopplerBins, dopplerBinned = dopplerBinned)
    dp.makePlot(dopplerBins,dopplerBinned, bins, binned)
    

#    fileName = '2012Apr24_1625_39binning.npz'
#    f = np.load(fileName)
#    binned = f['binned']
#    bins = f['bins']
#    dopplerBins = f['dopplerBins']
#    dopplerBinned = f['dopplerBinned']
#    makePlot(dopplerBins, dopplerBinned, bins, binned)

    