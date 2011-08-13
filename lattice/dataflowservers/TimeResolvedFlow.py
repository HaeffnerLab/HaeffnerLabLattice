'''
Created on Aug 12, 2011

@author: Michael Ramm
'''
from labrad.server import LabradServer, setting
from labrad.types import Error
from twisted.internet.defer import Deferred, returnValue, inlineCallbacks
from twisted.internet import reactor
from twisted.internet.threads import deferToThread
import numpy
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib import pyplot


#IMPROVE ON:
#handling of data_vault not found (wait for it to connect)

class TimeResolvedFlow( LabradServer):
    
    name = 'TimeResolvedFlow'
    @inlineCallbacks
    def initServer(self):
    #improve on this to start in arbitrary order
       self.dv = yield self.client.data_vault
       self.t = yield self.client.timeresolvedfpga
       ####self.dp = yield self.client.dataProcessor
       ####self.pbox = yield self.client.paulsbox
       self.saveFolder = ['','Time Resolved Counts']
       self.dataSet = 'CompressedCounts'
       self.fftSet = 'FFT'
       self.timelength = 0.010
       self.shouldRun = False
       self.figure = pyplot.figure()
       
    def makeNewDataSet(self):
        dir - self.saveFolder
        name = self.dataSet
        yield self.dv.cd(dir, True)
        yield self.dv.new(name, [('t', 'num')], [('KiloCounts/sec','866 ON','num'),('KiloCounts/sec','866 OFF','num'),('KiloCounts/sec','Differential Signal','num')])
        yield self.addParameters()
        yield self.dv.new()
    
    @setting(0, 'Set Save Folder', folder = '*s', returns = '')
    def setSaveFolder(self,c , folder):
        if self.shouldRun: raise("Please Stop Process First")
        yield self.dv.cd(folder, True)
        self.saveFolder = folder
    
    @setting(1, 'Start New Dataset', setName = 's', returns = '')
    def setNewDataSet(self, c, setName):
        if self.shouldRun: raise("Please Stop Process First")
        self.dataSet = setName
        yield self.makeNewDataSet()
            
    @setting( 2, returns = '' )
    def startLiveFFT( self, c):
        """
        Start recording Time Resolved Counts into Data Vault
        """
        self.shouldRun = True
        reactor.callLater( 0, self.doLiveFFT )
    
    @setting( 3, returns = '')
    def stopLiveFFT(self,c):
        """
        Stop recording Time Resolved Counts into DataVault
        """
        self.shouldRun = False

    @setting(5, returns = 'b')
    def isRunning(self,c):
        """
        Returns whether or not currently recording
        """
        return self.shouldRun
        
    @setting(6, returns = 's')
    def currentDataSet(self,c):
        return self.dataSet
    
    @setting(7, 'Set Time Length', timelength = 'v')
    def setTimeLenght(self, c, timelength):
        self.timelength = timelength
               
    @inlineCallbacks
    def doLiveFFT(self):
        if self.shouldRun:
            yield self.t.set_time_length(self.timelength)
            yield self.t.perform_time_resolved_measurement()
            (arrayLength, timeLength, timeResolution), measuredData = yield self.t.get_result_of_measurement()
            measuredData = measuredData.asarray
            yield self.saveResult(arrayLength, timeLength, timeResolution, measuredData)
            (freqs, ampl) = yield deferToThread(self.process, arrayLength, timeLength, timeResolution, measuredData)
            del(measuredData)
            #yield deferToThread(self.plot, freqs,ampl)
            del(freqs,ampl)
            print 'starting again'
            reactor.callLater(0,self.doLiveFFT)
    
    @inlineCallbacks
    def saveResult(self, arrayLength, timeLength, timeResolution, measuredData):
        yield None
        #### implement this
    
    def plot(self, x, y):
        import time
        t = time.time()
        self.figure.clf()
        pyplot.plot(x,y)
        pyplot.savefig('test')
        print time.time() - t
        print 'NEW'
    
    def process(self, arrayLength, timeLength, timeResolution, measuredData):
        positionsNZ = measuredData[0]
        elems = measuredData[1]
        #the following if faster but equivalent to binary conversion using the bitarray module
        result = numpy.zeros(( arrayLength, 16), dtype = numpy.uint8)          
        elems = map(self.converter , elems);
        result[positionsNZ] = elems
        del(positionsNZ)
        del(elems)
        result = result.flatten()
        fft = numpy.fft.rfft(result) #returns nice form, faster than fft for real inputs
        freqs = numpy.fft.fftfreq(result.size, d = float(timeResolution))
        freqs = numpy.abs(freqs[0:result.size/2 + 1])
        del(result)
        ampl = numpy.abs(fft)
        del(fft)
        return (freqs, ampl)    
    
    @staticmethod
    #goes from 255 to [0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1]
    def converter(x):
        str = bin(x)[2:].zfill(16)
        l = [int(s) for s in str]
        return l
            
if __name__ == "__main__":
    from labrad import util
    util.runServer( TimeResolvedFlow() )