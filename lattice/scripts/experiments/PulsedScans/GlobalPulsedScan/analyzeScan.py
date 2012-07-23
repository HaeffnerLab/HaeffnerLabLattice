import numpy
import time
from scipy import optimize

class AnalyzeScan():
    ''''
     Analyzes 110DP frequency scan
     '''
    
    def __init__(self, parent, timetags):

        self.parent = parent
        
        freqs = self.parent.seq.parameters.readout_freq_list
        start = self.parent.seq.parameters.startReadout
        stop = self.parent.seq.parameters.stopReadout
        cycleTime = self.parent.seq.parameters.cycleTime
      
        countsFreqArray = numpy.zeros(len(freqs)) # an array of total counts for each frequency      
        
        for j in range(len(freqs)):
            startTime = (cycleTime*j + start)
            stopTime = (cycleTime*j + stop)
            counts = numpy.count_nonzero( numpy.logical_and(timetags >= startTime, timetags <= stopTime) )
            countsFreqArray[j] = counts
        
        countsFreqArray = countsFreqArray / (stop - start) / float(self.parent.expP.iterations)
        # Add to the data vault
        self.parent.dv.new('Counts',[('Freq', 'MHz')],[('Counts','Arb','Arb')] )
        self.parent.dv.add(numpy.vstack((freqs,countsFreqArray)).transpose())
        self.parent.dv.add_parameter('Window',['110DP Frequency Scan'])
        self.parent.dv.add_parameter('plotLive',True)         
        
        self.fitModel(freqs, countsFreqArray)
          
    def fit(self, function, parameters, y, x = None):  
        solutions = [None]*len(parameters)
        def f(params):
            i = 0
            for p in params:
                solutions[i] = p
                i += 1
            return (y - function(x, params))
        if x is None: x = numpy.arange(y.shape[0])
        optimize.leastsq(f, parameters)
        return solutions
    
    def fitFunction(self, x, p):
        """p = [center, scale, offset] """   
        fitFunc = p[2] + (1/numpy.pi)*(p[1]/((x - p[0])**2 + (p[1])**2))
        return fitFunc

    def fitModel(self, freqs, countsFreqArray):
        scale = numpy.max(countsFreqArray) - numpy.min(countsFreqArray)
        center = numpy.median(freqs)
        offset = numpy.min(countsFreqArray)
        
        center, scale, offset = self.fit(self.fitFunction, [center, scale, offset], countsFreqArray, freqs)
        print 'Center: ', center
        print 'Scale: ', scale
        print 'Offset: ', offset
        
        xmodel = numpy.arange(numpy.min(freqs), numpy.max(freqs), 0.05)
        model = self.fitFunction(xmodel, [center, scale, offset])
        
        self.parent.dv.new('Model',[('Freq', 'MHz')],[('Counts','Arb','Arb')] )
        self.parent.dv.add(numpy.vstack((xmodel,model)).transpose())
        self.parent.dv.add_parameter('Window',['110DP Frequency Scan'])
        self.parent.dv.add_parameter('plotLive',True)
        