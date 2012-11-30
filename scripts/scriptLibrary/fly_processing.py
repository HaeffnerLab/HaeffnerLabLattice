import numpy

class Binner():
    '''Helper class for binning received timetags'''
    def __init__(self, totalWidth, binWidth, offset = 0):
        assert binWidth > 0.0, "Bin width must be positive"
        self.averaged = 0
        self.offset = offset
        self.binWidth = binWidth
        binNumber = int(totalWidth / binWidth)
        self.binArray = self.offset + binWidth * numpy.arange(binNumber + 1)
        self.binned = numpy.zeros(binNumber)
    
    def add(self, newData, added = 1):
        newbinned = numpy.histogram(newData, self.binArray )[0]
        self.binned += newbinned
        self.averaged += added
    
    def getBinned(self, normalize = True):
        if normalize:
            binned = self.binned / float(self.binWidth)
            if not self.averaged == 0:
                binned = binned / float(self.averaged)
        return (self.binArray[0:-1], binned)

class Splicer():
    '''Helper class for maintaining a list of timetags during a readout period'''
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.counts = []
    
    def add(self, newData):
        counts = numpy.count_nonzero((self.start <= newData) * (newData <= self.end))
        counts = counts / float(self.end - self.start) #normalize
        self.counts.append(counts)
        
    def getList(self):
        counts = numpy.array(self.counts)
        enumer = numpy.arange(counts.size)
        together = numpy.vstack((enumer, counts)).transpose()
        return together
    
    def getPercentage(self, threshold):
        counts = numpy.array(self.counts)
        below = numpy.count_nonzero(counts <= threshold) / float(counts.size)
        above = numpy.count_nonzero(counts > threshold) / float(counts.size)
        return (below, above)
    
    def getHistogram(self, numberBins = 50):
        counts = numpy.array(self.counts)
        binned,bins = numpy.histogram(counts, bins = numberBins)
        return (bins[0:-1],binned)