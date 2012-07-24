import sys; 
import labrad
import numpy
import time
from scripts.scriptLibrary import dvParameters 
from scripts.PulseSequences.pulsedScan110DP_list import PulsedScan as sequence
from fly_processing import Interpolator
from analyzeScan import AnalyzeScan

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
    
    def __setitem__(self, key, val):
        self.__dict__[key] = val
    
    def toDict(self):
        return self.__dict__
    
class scan():
    ''''
    Performs frequency scan of 110DP, for each frequency calculates the probability of the ion going dark. Plots the result.
    
    Possible improvements:
        if exceeds 32K counts per iterations of cycles, be able to repeat that multiple times for a given frequency. allow for this change in data analysis
        multiple data processing, including histogram to get the threshold
    '''
    experimentName = 'scan110DP'
    
    def __init__(self, seqParams, exprtParams):
        #connect and define servers we'll be using
        self.cxn = labrad.connect()
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.dv = self.cxn.data_vault
        self.pulser = self.cxn.pulser
        self.seqP = Bunch(**seqParams)
        self.expP = Bunch(**exprtParams)
        
    def initialize(self):
        #directory name and initial variables
        self.dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())
        self.directory = ['','Experiments', self.experimentName, self.dirappend]
        #saving
        self.dv.cd(self.directory ,True )
        self.dv.new('timetags',[('Freq', 'MHz')],[('Time','Sec','Sec')] )
        self.programPulser()
        self.setupLogic()
        
    def setupLogic(self):
        self.pulser.switch_auto('axial',  True) #axial needs to be inverted, so that high TTL corresponds to light ON
        self.pulser.switch_auto('110DP',  False) #high TTL corresponds to light OFF
        self.pulser.switch_auto('866DP', False) #high TTL corresponds to light OFF
        self.pulser.switch_auto('729DP', True)
        self.pulser.switch_manual('crystallization',  False)
    
    def programPulser(self):
        seq = sequence(self.pulser)
        self.pulser.new_sequence()
        seq.setVariables(**params)
        seq.defineSequence()
        self.pulser.program_sequence()
        self.seqP['recordTime'] = seq.parameters.recordTime
        self.seq = seq
    
    def run(self):
        self.initialize()
        self.sequence()
        self.finalize()
        print 'DONE {}'.format(self.dirappend)
        
    def sequence(self):
        xP = self.expP
        self.pulser.reset_timetags()
        self.pulser.start_number(xP.iterations)
        self.pulser.wait_sequence_done(1000.0) #seconds
        self.pulser.stop_sequence()
        timetags = self.pulser.get_timetags().asarray
        print 'got {} timetags'.format(timetags.size)
        #saving timetags
        ones = numpy.ones_like(timetags)
        self.dv.add(numpy.vstack((ones,timetags)).transpose())
        analyzeScan = AnalyzeScan(self, timetags)
        #self.analyzeScan(timetags)
    
#    def analyzeScan(self, timetags):
#        
#        freqs = self.seq.parameters.readout_freq_list
#        start = self.seq.parameters.startReadout
#        stop = self.seq.parameters.stopReadout
#        cycleTime =  self.seq.parameters.cycleTime
#      
#        countsFreqArray = numpy.zeros(len(freqs)) # an array of total counts for each frequency      
#        
#        for j in range(len(freqs)):
#            startTime = (cycleTime*j + start)
#            stopTime = (cycleTime*j + stop)
#            counts = len(numpy.where((timetags >= startTime) & (timetags <= stopTime))[0])
#            countsFreqArray[j] = counts
#        
#        # Add to the data vault
#        self.dv.new('Counts',[('Freq', 'MHz')],[('Counts','Arb','Arb')] )
#        self.dv.add(numpy.vstack((freqs,countsFreqArray)).transpose())
#        self.dv.add_parameter('Window',['110DP Calibrated Scan'])
#        self.dv.add_parameter('plotLive',True)
        
    def finalize(self):
        for name in ['axial', '110DP']:
            self.pulser.switch_manual(name)
        #save information to file
        measureList = ['trapdrive','endcaps','compensation','dcoffsetonrf','cavity397','cavity866','multiplexer397','multiplexer866','axialDP', 'pulser']
        measuredDict = dvParameters.measureParameters(self.cxn, self.cxnlab, measureList)
        dvParameters.saveParameters(self.dv, measuredDict)
        dvParameters.saveParameters(self.dv, self.seqP.toDict())
        dvParameters.saveParameters(self.dv, self.expP.toDict())
        
    def __del__(self):
        self.cxn.disconnect()
    
if __name__ == '__main__':
    #separate connection for getting interpolation
    cxn = labrad.connect()
    dv = cxn.data_vault
    dv.cd(['','Calibrations', 'Double Pass 110DP'])
    dv.open(48)
    data = dv.get().asarray
    freq_interp =  data[:,0]
    ampl_interp = data[:,1]
    cxn.disconnect()
    interp = Interpolator(freq_interp, ampl_interp)
    
    freq_min = 90.0
    freq_max = 130.0
    freq_step = 1.0
    
    
    freqs = numpy.arange(freq_min, freq_max + freq_step, freq_step)
    freqs = numpy.clip(freqs, freq_min, freq_max)
    ampls = interp.interpolated(freqs)
    freqs = freqs.tolist()
    ampls = ampls.tolist()
    
    #print zip(freqs,ampls)

    params = {
            'cooling_time':5.0*10**-3,
            'cooling_freq':90.0,
            'cooling_ampl':-11.0,
            'readout_time':200.0*10**-6,
            'switch_time':100.0*10**-6,
            'readout_ampl_list':ampls,
            'readout_freq_list':freqs,
            }
    
    exprtParams = {
        'iterations':2
        }
    exprt = scan(params,exprtParams)
    exprt.run()