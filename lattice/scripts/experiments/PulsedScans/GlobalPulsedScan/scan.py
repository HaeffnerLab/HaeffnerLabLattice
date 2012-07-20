import sys; 
sys.path.append('/home/lattice/LabRAD/lattice/scripts')
sys.path.append('/home/lattice/LabRAD/lattice/PulseSequences')
sys.path.append('C:\Users\lattice\Desktop\LabRAD\lattice\scripts')
import labrad
import numpy
import time
from scriptLibrary import dvParameters 
from PulseSequences.pulsedScan110DP import PulsedScan as sequence

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
        self.pulser.wait_sequence_done(self.expP.iterations/16)
        self.pulser.stop_sequence()
        timetags = self.pulser.get_timetags().asarray
        print 'got {} timetags'.format(timetags.size)
        #saving timetags
        ones = numpy.ones_like(timetags)
        self.dv.add(numpy.vstack((ones,timetags)).transpose())
        self.analyzeScan(timetags)
    
    def analyzeScan(self, timetags):
        
        freqs = self.seq.parameters.freqs
        start = self.seq.parameters.startReadout
        stop = self.seq.parameters.stopReadout
        cycleTime =  self.seq.parameters.cycleTime
      
        countsFreqArray = numpy.zeros(len(freqs)) # an array of total counts for each frequency      
        
        for j in range(len(freqs)):
            startTime = (cycleTime*j + start)
            stopTime = (cycleTime*j + stop)
            counts = len(numpy.where((timetags >= startTime) & (timetags <= stopTime))[0])
            countsFreqArray[j] = counts
        
        # Add to the data vault
        self.dv.new('Counts',[('Freq', 'MHz')],[('Counts','Arb','Arb')] )
        self.dv.add(numpy.vstack((freqs,countsFreqArray)).transpose())
        self.dv.add_parameter('plotLive',True)      
        
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
  
    params = {
            'cooling_time':1.0*10**-3,
            'cooling_freq':100.0,
            'cooling_ampl':-11.0,
            'readout_time':100.0*10**-6,
            'readout_ampl':-11.0,
            'switch_time':100.0*10**-6,
            'freq_min':90.0,
            'freq_max':110.0,
            'freq_step':1.0
            }
    exprtParams = {
        'iterations':50
        }
    exprt = scan(params,exprtParams)
    exprt.run()