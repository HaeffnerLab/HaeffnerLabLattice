import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
from scipy.cluster.vq import whiten, kmeans, vq

class freqscan():
    '''Allows to plot a histogram of the timetags between self.start and self.end'''
    def __init__(self, start, end, threshold = None, dv = None):
        self.start = start
        self.end = end
        self.threshold = threshold
        self.dv = dv
        self.cntxprob = self.dv.context()
        self.dv.new('Spectrum',[('Freq', 'MHz')],[('Prob','Arb','Prob'),('Fluor','Count/Sec','Mean Fluor')] , context = self.cntxprob )
        self.dv.add_parameter('Window',['Spectrum729'], context = self.cntxprob)
        self.dv.add_parameter('plotLive',True, context = self.cntxprob)

    def addTrace(self, timetags):
        self.timetags = timetags
        
    def processTraces(self):
        self.timetags = self.timetags.transpose()
        self.freqs = np.unique(self.timetags[0])
        for freq in self.freqs:
            tags = self.timetags[1][np.where(self.timetags[0] == freq)] #get all timetags for a specific frequency
            ix = np.where(np.ediff1d(tags) < 0 )[0] #when the next sequence starts, timetags decrease
            split = np.split(tags, ix + 1)
            counts = []
            for iter in split:
                cnt = np.count_nonzero( (iter <= self.end) * (iter >= self.start))
                counts.append(cnt)
            counts = np.array(counts) / (self.end - self.start) #rate in counts / sec
            mean = np.mean(counts)
            prob = -1.0
            if self.threshold is None:
                self.threshold = self.clusterkmeans(counts)    
            if self.threshold is not None:
                prob = np.count_nonzero(counts < self.threshold) / float(len(split))
            self.addPlot(freq,mean,prob)
    
    def clusterkmeans(self, counts):
        wh = whiten(counts) #normalizes the counts for easier clustering
        scale = counts[0] / wh[0]
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
    
    def addPlot(self, freq, mean, prob):
        self.dv.add((freq, prob, mean), context = self.cntxprob)

class data_process():
    def __init__(self, cxn , dataset, directory, processNames):
        self.dv = cxn.data_vault
        self.dataset = dataset
        self.directory = directory
        self.processNames = processNames
        self.availableProcesses = ['freqscan']
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
        self.dv.open(1)
    
    def loadDataVault(self):
        self.navigateDirectory()
        self.loadParameters()
        self.createProcesses()
        timetags = self.dv.get().asarray
        self.addAll(timetags)
    
    def createProcesses(self):
        if 'freqscan' in self.processNames:
            startReadout =  self.params.get('startReadout') 
            stopReadout = self.params.get('stopReadout') 
            threshold = self.params.get('threshold') 
            self.process.append(freqscan(startReadout, stopReadout, threshold = threshold, dv = self.dv))
        
    def loadParameters(self):
        for par in ['startReadout', 'stopReadout','backgroundMeasure', 'initial_cooling', 'optical_pumping','rabitime','readout_time','repump854','repumpPower']:
            self.params[par] =  self.dv.get_parameter(par)
    
    def addAll(self, trace):
        for pr in self.process:
            pr.addTrace(trace)

    def processAll(self):
        for pr in self.process:
            pr.processTraces()

if __name__ == '__main__':
#    dataset = '2012Apr16_2133_32'
#    directory = ['','Experiments','scan729']
#    import labrad
#    cxn = labrad.connect()
#    dp = data_process(cxn, dataset, directory, ['freqscan'])
#    #dp.addParameter('threshold', 100)
#    dp.loadDataVault()
#    dp.processAll()
#    print 'done'
    pass