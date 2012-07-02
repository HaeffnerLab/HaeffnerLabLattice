import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
from scipy.cluster.vq import whiten, kmeans, vq

class histogramTimetags():
    '''Allows to plot a histogram of the timetags between self.start and self.end'''
    def __init__(self, start, end, bins = 50, title = None, threshold = None, readout_time = None ):
        self.start = start
        self.end = end
        self.bins = bins
        self.threshold = threshold
        self.title = title
        self.readout_time = readout_time
        self.counts = []

    def addTrace(self, timetags):
        counts = np.count_nonzero((self.start <= timetags) * (timetags <= self.end))
        counts = counts / float(self.readout_time) #normalize
        self.counts.append(counts)
        
    def processTraces(self):
        if self.threshold is None:
            self.threshold = self.clusterkmeans()    
        if self.threshold is not None:
            self.analyzeThreshold(self.threshold)
        self.plot()
    
    def clusterkmeans(self):
        wh = whiten(self.counts) #normalizes the counts for easier clustering
        scale = self.counts[0] / wh[0]
        #compute kmeans for  k = 1,2 compare the distortions and choose the better one
        one = kmeans(wh, 1)
        two = kmeans(wh, 2)
        if one[1] < two[1]:
            print 'found only one cluser'
            threshold = None
        else:
            km = two
            threshold = scale * km[0].mean() #set threshold to be the average of two centers
        return threshold

    def analyzeThreshold(self, threshold):
        counts = np.array(self.counts)
        below = np.count_nonzero(counts <= threshold) / float(counts.size)
        above = np.count_nonzero(counts > threshold) / float(counts.size)
        print '{0}% of samples are below {1} '.format(100 * below, threshold)
        print '{0}% of samples are above {1} '.format(100 * above, threshold)
        
    def plot(self):
        figure = pyplot.figure()
        figure.clf()
        if self.title is not None:
            pyplot.suptitle(self.title)
        pyplot.hist(self.counts, self.bins, range  = (0, max(self.counts)))
        pyplot.show()

class data_process():
    def __init__(self, cxn , dataset, directory, processNames):
        self.dv = cxn.data_vault
        self.dataset = dataset
        self.directory = directory
        self.processNames = processNames
        self.availableProcesses = ['histogram']
        self.confirmProcesses()
        self.process = []
        self.params = {}
    
    def addParameter(self, name, value):
        self.params[name] = value
    
    def confirmProcesses(self):
        for pr in self.processNames:
            if pr not in self.availableProcesses: raise Exception ("Process not found")
            
    def navigateDirectory(self):
        self.dv.cd(self.directory)
        self.dv.cd(self.dataset)
    
    def loadDataVault(self):
        self.navigateDirectory()
        self.loadParameters()
        self.createProcesses()
        self.dv.cd('timetags')
        traces = len(self.dv.dir()[1])
        if not traces: raise Exception("No saved timetags")
        for trace in range(1, traces+1):
            print trace
            self.dv.open(int(trace))
            timetags = self.dv.get().asarray[:,0]
            self.addAll(timetags)
    
    def createProcesses(self):
        if 'histogram' in self.processNames:
            initial_cooling = self.params['initial_cooling']
            heat_delay = self.params['heat_delay']
            axial_heat = self.params['axial_heat']
            readout_delay = self.params['readout_delay']
            readout_time = self.params['readout_time']
            startReadout =  (axial_heat + initial_cooling + heat_delay + axial_heat + readout_delay ) 
            stopReadout = startReadout + readout_time
            threshold = self.params.get('threshold') 
            self.process.append(histogramTimetags(startReadout, stopReadout, title = self.dataset, threshold = threshold, readout_time = readout_time))
        
    def loadParameters(self):
        self.dv.open(1)    
        for par in ['initial_cooling', 'heat_delay', 'axial_heat','readout_delay','readout_time']:
            self.params[par] =  self.dv.get_parameter(par)
    
    def addAll(self, trace):
        for pr in self.process:
            pr.addTrace(trace)

    def processAll(self):
        for pr in self.process:
            pr.processTraces()

if __name__ == '__main__':
    dataset = '2012Jun21_1644_58'
    directory = ['','Experiments','LatentHeat_no729_autocrystal']
    import labrad
    cxn = labrad.connect()
    dp = data_process(cxn, dataset, directory, ['histogram'])
    dp.addParameter('threshold', 100)
    dp.loadDataVault()
    dp.processAll()
    print 'done'