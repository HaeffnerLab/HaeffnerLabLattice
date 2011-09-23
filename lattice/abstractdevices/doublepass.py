from labrad.server import LabradServer, setting, Signal
from twisted.internet.defer import inlineCallbacks, returnValue

class doublePass(object):
    def __init__(self):
        self.freq = None
        self.ampl = None
        self.output = None
        self.amplOffset = 0
        self.freqFunc = None #function for setting the frequency in MHZ
        self.amplFunc = None #function for setting the amplitude in DM
        self.outputFunc = None #function for setting the output using True/False
        self.freqToCalibAmpl = None #function to get calibrated amplitude for the given frequency
         
    @inlineCallbacks
    def populateInfo(self):
        self.freq = yield self.freqFunc()
        self.ampl = yield self.amplFunc()
        self.output = yield self.outputFunc()
    
    @inlineCallbacks
    def frequency(self, freq):
        if freq is not None:
            yield self.freqFunc(freq)
            self.freq = freq
        returnValue( self.freq)
    
    @inlineCallbacks
    def amplitude(self, ampl):
        if ampl is not None:
            yield self.amplFunc(ampl)
            self.ampl = amplitude
        returnValue( self.ampl)
    
    @inlineCallbacks
    def output(self, output):
        if output is not None:
            yield self.outputFunc(output)
            self.output = output
        returnValue( self.output)

    @inlineCallbacks
    def freqCalibPower(self, freq):
        yield self.frequency(freq)
        calibAmpl = self.freqToCalibAmpl(freq) + self.amplOffset
        yield self.amplitude(calibAmpl) 
        returnValue ((self.freq, self.ampl))
    
    @inlineCallbacks
    def amplitudeOffset(self, offset):
        self.amplOffset = offset
        yield self.freqCalibPower(self.freq)
        returnValue ((self.freq, self.ampl))
        
class global397(doublePass):
    def __init__(self, cxn):
        super(global397,self).__init__()
        self.selectFuncs(cxn)
    
    @inlineCallbacks
    def selectFuncs(self, cxn):
        server = cxn.rohdeschwarz_server
        yield server.select_device('lattice-pc GPIB Bus - USB0::0x0AAD::0x0054::104542')
        self.freqFunc = server.frequency
        self.amplFunc = server.amplitude
        self.outputFunc = server.output
        yield self.populateInfo()
    
    #no calibration, that is no amplitude dependence on frequency
    def freqToCalibAmpl(self, freq):
        return self.ampl

class doublePassServer( LabradServer ):
    name = 'Double Pass'
    
    def initServer( self ):
        self.createDict()
    
    def createDict(self):
        self.d = {'global397':global397(self.client)
                  }
        
    @setting(0, "Get Double Pass List", returns = '*s')
    def getDPList(self, c,):
        """Returns the list of available double passes"""
        return self.d.keys()
    
    @setting(1, "Select", name = 's', returns = '')
    def selectDP(self, c, name):
        """Select Double Pass in the current context"""
        if name not in self.d.keys(): raise Exception("No such double pass")
        c['doublePass'] = self.d[name]
    
    @setting(2, "Frequency", freq ='v', returns = 'v')
    def frequency(self, c, freq = None):
        """Sets the frequency of the selected double pass, returns set frequency"""
        dp = self.getDP(c)
        setfreq = dp.frequency(freq)
        return setfreq

    @setting(3, "Frequency Calibrated Amplitude", freq = 'v', returns = '(vv)')
    def freqCalibPower(self, c, freq):
        dp = self.getDP(c)
        (setfreq, setamplitude) = dp.frequencyCalibPower(freq)
        return (setfreq, setamplitude)
        
    @setting(4, "Amplitude", amplitude = 'v', returns ='v')
    def amplitude(self, c, amplitude = None):
        """Sets the amplitude of the selected double pass, returns set amplitude"""
        dp = self.getDP(c)
        print dp
        setamplitude = dp.amplitude(amplitude)
        return setamplitude
    
    @setting(5, "Amplitude Offset", offset = 'v', returns = '(vv)')
    def amplitudeOffset(self, c, offset = None):
        """Sets the difference between the desired power and the maximum power available from the calibration"""
        if offset >= 0: raise Exception ("offset must be negatve")
        dp = self.getDP(c)
        (setoffset,setpower) = dp.amplitudeoffset(offset)
        return (setoffset,setpower)
    
    @setting(6, "Output", output = 'b', returns = 'b')
    def output(self, c, output):
        """Sets the output to true/false for the desired double pass"""
        dp = self.getDP(c)
        output = dp.output(output)
        return output
    
    def getDP(self, context):
        if not 'doublePass' in context.keys(): raise Exception ('Double Pass not selected')
        return context['doublePass']
    
if __name__ == "__main__":
    from labrad import util
    util.runServer(doublePassServer())
