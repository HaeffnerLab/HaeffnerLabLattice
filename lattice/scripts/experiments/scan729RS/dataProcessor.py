import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot
from scipy.cluster.vq import whiten, kmeans, vq

class freqscan():
    '''Allows to plot a histogram of the timetags between self.start and self.end'''
    def __init__(self, start, end, dv, directory, threshold = None):
        self.start = start
        self.end = end
        self.threshold = threshold
        self.dv = dv
        self.cntxprob = self.dv.context()
        self.dv.cd(directory, context = self.cntxprob)
        self.madePlot = False
   
        self.d = {}
        self.allcounts = []

    def setThreshold(self, threshold):
        self.threshold = threshold
    
    def addFrequency(self, freq, tags, addToPlot = False):
        split = self._splitTags(tags)
        counts = self._countReadout(split)
        self.d[freq] = counts
        self.allcounts.extend(counts)
        if addToPlot:
            mean,prob = self._extractProb(counts)
            self.addPlot(freq,mean,prob)
    
    def _extractProb(self, counts):
        counts = np.array(counts)
        mean = counts.mean() / (self.end - self.start)
        try:
            prob = np.count_nonzero(counts < self.threshold) / float(len(counts))
        except:
            print 'ERROR: threshold not set'
            prob = -1.0
        return mean, prob
    
    def _splitTags(self, tags):
        '''splits timetags from multiple back to back sequences into a list timetags separated by sequences'''
        ix = np.where(np.ediff1d(tags) < -1*10**-3 )[0] #when the next sequence starts, timetags decrease #####fix this 
        split = np.split(tags, ix + 1)
        return split
    
    def _countReadout(self, split):
        '''takes a list of timetag sequences and returns the corresponding list of how many timetags occured during readout'''
        counts = []
        for iter in split:
            cnt = np.count_nonzero( (iter <= self.end) * (iter >= self.start))
            counts.append(cnt)
        return counts

    def _organizRaw(self, data):
        '''takes the data and puts it into a dictionary by frequency. The key is an array of total counts recorded during readout'''
        timetags = data.transpose()
        freqs = np.unique(timetags[0])
        for freq in freqs:
            tags = timetags[1][np.where(timetags[0] == freq)] #get all timetags for a specific frequency
            split = self._splitTags(tags)
            counts = self._countReadout(split)
            self.d[freq] = counts
            self.allcounts.extend(counts)
        return freqs
            
    def addAllData(self, data, addToPlot = False):
        freqs = self._organizRaw(data)
        if addToPlot:
            for freq in freqs:
                counts = self.d[freq]
                mean,prob = self._extractProb(counts)
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
        try:
            self.dv.add((freq, prob), context = self.cntxprob)
        except:
            #need to make the plot first
            self.dv.new('Spectrum',[('Freq', 'MHz')],[('Prob','Arb','Prob')] , context = self.cntxprob )
            self.dv.add_parameter('Window',['Spectrum729'], context = self.cntxprob)
            self.dv.add_parameter('plotLive',True, context = self.cntxprob)
            self.dv.add((freq, prob), context = self.cntxprob)
        
    def makeHistPlot(self, counts = None):
        if counts is None: counts = self.allcounts
        binned,edges = np.histogram(counts, bins = 30)
        edges = edges[:-1] #excluding last edge
        self.dv.new('Histogram',[('Fluor', 'Counts/sec')],[('Occurance','Num','Num')] , context = self.cntxprob )
        self.dv.add_parameter('Window',['CountHistogram'], context = self.cntxprob)
        self.dv.add_parameter('plotLive',True, context = self.cntxprob)
        data = np.vstack((edges,binned)).transpose()
        self.dv.add(data, context = self.cntxprob)
                  
if __name__ == '__main__':
    dataset = '2012Jun19_1614_30'
    directory = ['','Experiments','scan729', dataset]
    threshold = 10
    
    
    import labrad
    cxn = labrad.connect()
    dv = cxn.data_vault
    dv.cd(directory)
    dv.open('00001 - timetags')
    startReadout = dv.get_parameter('startReadout')
    stopReadout = dv.get_parameter('stopReadout')
    
    dp =  freqscan(startReadout, stopReadout, dv, directory, threshold)
    data = dv.get().asarray
    dp.addAllData(data, addToPlot = True)
    dp.makeHistPlot()
    print 'Done running analysis'