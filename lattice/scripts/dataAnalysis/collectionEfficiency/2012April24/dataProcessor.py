import numpy as np
import labrad
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

class dataProcessor():
    
    binTime = 40.0*10**-9 #fpga resolution
    dopplerBinTime = 1.0*10**-3
    
    def __init__(self, params):
        self.repumpD = params['repumpD']
        self.repumpDelay = params['repumpDelay']
        self.exciteP = params['exciteP']
        self.finalDelay = params['finalDelay']
        self.dopplerCooling = params['dopplerCooling']
        self.iterDelay = params['iterDelay']
        self.iterationsCycle = params['iterationsCycle']
        self.cycleTime = self.repumpD + self.repumpDelay + self.exciteP + self.finalDelay
        binNumber = int(self.cycleTime / self.binTime)
        self.bins = self.binTime * np.arange(binNumber + 1)
        self.binned = np.zeros(binNumber)
        dopplerBinNumber = int(self.dopplerCooling / self.dopplerBinTime)
        self.dopplerBins = self.dopplerBinTime * np.arange(dopplerBinNumber + 1)
        self.dopplerBinned = np.zeros(dopplerBinNumber)
    
    def addTimetags(self, timetags):
        sliced = self.sliceArr(timetags, start = self.dopplerCooling + self.iterDelay, duration = self.cycleTime, cyclenumber = self.iterationsCycle,  cycleduration = self.cycleTime)
        self.binned += np.histogram(sliced,  self.bins)[0] / float(self.iterationsCycle)
        doppler = self.sliceArr(timetags, start = 0, duration = self.dopplerCooling + self.iterDelay)
        self.dopplerBinned += np.histogram(doppler, self.dopplerBins)[0]
    
    def normalize(self, repeatitions):
        self.binned = self.binned / self.binTime
        self.binned = self.binned / float(repeations)
        self.dopplerBinned = self.dopplerBinned / float(repeations)
        self.dopplerBinned = self.dopplerBinned / self.dopplerBinTime
        
    def save(self, dataset):
        np.savez('{}binning'.format(dataset), binned = self.binned, bins = self.bins, dopplerBins = self.dopplerBins, dopplerBinned = self.dopplerBinned)
    
    def load(self, dataset):
        pass
#    fileName = '2012Apr24_1625_39binning.npz'
#    f = np.load(fileName)
#    binned = f['binned']
#    bins = f['bins']
#    dopplerBins = f['dopplerBins']
#    dopplerBinned = f['dopplerBinned']
#    makePlot(dopplerBins, dopplerBinned, bins, binned)
    
    def makePlot(self):
        pyplot.figure()
        ax = pyplot.subplot(121) 
        pyplot.plot(self.dopplerBins[0:-1],self.dopplerBinned)
        pyplot.title('Doppler Cooling')
        pyplot.xlabel('Sec')
        pyplot.ylabel('Counts/Sec')
        pyplot.subplot(122, sharey = ax) 
        pyplot.title('Experimental Cycle')
        pyplot.plot(self.bins[0:-1],self.binned)
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
    #objects we need
    cxn = labrad.connect('192.168.169.254', password = 'lab')
    dv = cxn.data_vault
    #naviagate to the dataset
    dv.cd(['', 'Experiments', experiment, dataset, 'timetags'])
    repeations = len(dv.dir()[1])
    
    params = {
          'dopplerCooling':100e-3,
          'iterDelay':1e-6,
          'iterationsCycle': 250,
          'repumpD':5.0*10**-6,#
          'repumpDelay':1.0*10**-7,
          'exciteP':1.0*10**-6,
          'finalDelay':5.0*10**-6,
              }

    dp = dataProcessor(params)
    repeations = 50
    import time
    for i in range(1, repeations + 1):
        print 'opening', i
        time.sleep(.1)
        dv.open(i)
        timetags = dv.get().asarray
        dp.addTimetags(timetags)
    dp.normalize(repeations)
    #dp.save(dataset)
    dp.makePlot()