import numpy as np
import labrad
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot

class dataProcessor():

    def __init__(self, params):       
        self.pulsedTime = float(params['pulsedTime'])
        self.coolingTime = float(params['coolingTime'])
        self.switching = float(params['switching'])
        self.iterations = int(params['iterations'])
        self.cycleTime = float(params['cycleTime'])
    
    def addData(self, timetags):
        self.timetags = timetags
        self.addData = None
    
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
    
    def process(self):
        self.processBinning()
        self.processPowerScan()
    
    def processBinning(self):
        '''shows binning at the highest power'''
        times = self.timetags[:,1]
        powers = self.timetags[:,0]
        maxpower =  np.max(np.unique(self.timetags[:,0]))
        tags = times[np.where(powers == maxpower)]
        tags = np.mod(tags, self.cycleTime)
        binTime = 25.0*10**-6
        self.bins = np.arange(self.cycleTime / binTime) * binTime
        self.binned = np.histogram(tags, self.bins)[0]
        collectionTime = self.cycleTime * self.iterations
        self.binned = self.binned / (self.iterations * binTime) #Counts per sec
        
    def processPowerScan(self):
        '''plots the total number of differential counts during the pulsed times vs the power at the time of pulsing'''
        times = self.timetags[:,1]
        powers = self.timetags[:,0]
        self.pwrList =  np.unique(self.timetags[:,0])
        fluor = []
        for pwr in self.pwrList:
            tags = times[np.where(powers == pwr)]
            countsBackground = self.sliceArr(tags,  start = self.coolingTime + self.switching, duration =  self.pulsedTime, cyclenumber = self.iterations, cycleduration = self.cycleTime)
            countsSignal = self.sliceArr(tags,  start = self.coolingTime + self.switching + self.pulsedTime, duration =  self.pulsedTime, cyclenumber = self.iterations, cycleduration = self.cycleTime)
            bgsubtracted = countsSignal.size - countsBackground.size
            #converting to Counts/Sec
            collectionTime = self.pulsedTime * self.iterations
            bgsubtracted = bgsubtracted / float(collectionTime)
            fluor.append(bgsubtracted)
        self.fluor = np.array(fluor)
        
    def makePlot(self):
        pyplot.figure()
        ax = pyplot.subplot(121) 
        pyplot.plot(self.bins[0:-1],self.binned)
        pyplot.title('Max Power Average Iteration')
        pyplot.xlabel('Sec')
        pyplot.ylabel('Counts/Sec')
        pyplot.subplot(122, sharey = ax) 
        pyplot.title('Power Scan')
        pyplot.plot(self.pwrList, self.fluor)
        pyplot.xlabel('AO Power dBM')
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
    #dataset = '2012May11_1555_17'
    dataset = '2012May11_1644_53'
    experiment = 'pulsedScanAxialPower'
    #objects we need
    cxn = labrad.connect()
    dv = cxn.data_vault
    #naviagate to the dataset
    dv.cd(['', 'Experiments', experiment, dataset])
    dv.open(1)
    data = dv.get().asarray
    params = dict(dv.get_parameters())
    dp = dataProcessor(params)
    dp.addData(data)
    dp.process()
    dp.makePlot()