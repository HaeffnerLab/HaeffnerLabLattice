import numpy as np
import labrad
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
        self.addData = self.appendData
            
    def appendData(self, timetags):
        self.timetags = np.append(self.timetags, timetags)
    
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
        times = self.timetags[:,1]
        powers = self.timetags[:,0]
        self.pwrList =  np.unique(self.timetags[:,0])
        fluor = []
        for pwr in self.pwrList:
            tags = times[np.where(powers == pwr)]
            counts = self.sliceArr(tags,  start = self.coolingTime + self.switching, duration =  self.pulsedTime, cyclenumber = self.iterations, cycleduration = self.cycleTime)
            fluor.append(counts.size)
        self.fluor = np.array(fluor)
    
    def makePlot(self):
        pyplot.figure()
        pyplot.plot(self.pwrList, self.fluor)
        pyplot.title('Power Scan')
        pyplot.xlabel('Power dBM')
        pyplot.ylabel('Counts')
        pyplot.show()

if __name__ == '__main__':
    dataset = '2012Apr27_1614_10'
    #dataset = '2012Apr27_1620_25'
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