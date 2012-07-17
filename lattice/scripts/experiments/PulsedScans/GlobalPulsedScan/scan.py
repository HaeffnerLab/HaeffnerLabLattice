import sys; 
sys.path.append('/home/lattice/LabRAD/lattice/scripts')
sys.path.append('/home/lattice/LabRAD/lattice/PulseSequences')
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
#        self.setupAnalysis()
        
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
        
        """timetags is an array of timetags obtained during readout times (1 count per time tag) arranged by frequency in order of iteration
        
            NOTE: because the pulse sequence only records during readout time
        
            t1-1 -> timetag for iteration 1 - frequency 1
            t5-2 -> timetag for iteration 5 - frequency 2
        
           Ex: for two iterations and three frequencies  
           
               [t1-1, t1-1, t1-1, t1-2, t1-3, t1-3, t2-1, t2-2, t2-2, t2-2, t2-2, t2-3, t2-3]
               
               This example data means:
                   
                   Iteration 1:
                       3 counts for frequency 1
                       1 count for frequency 2
                       2 counts for frequency 3
                       
                   Iteration 2:
                       1 count for frequency 1
                       4 counts for frquency 2
                       3 counts for frequency 3
                
                   Total (iterations are summed):
                       4 counts for frequency 1
                       5 counts for frequency 2
                       5 counts for frequency 3
            
            Since these timetags are in sequential order for each iteration, one can determine where a new iteration begins because the timetags
            reset to a lower value periodically.
            
            The following procedure identifies the array positions (splicePoints) in timetags where a new iteration begins:
            
                timetags = [1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 1, 2, 3, 4, 5, 6, 1, 2, 3]
                
                subtract = [2, 3, 4, 5, 6, 1, 2, 3, 4, 1, 2, 3, 4, 5, 6, 1, 2, 3, 0]
                
                difference = [-1, -1, -1, -1, -1, 5, -1, -1, -1, 3, -1, -1, -1, -1, -1, 5, -1, -1, 3]
                
                signs = [-1, -1, -1, -1, -1, 1, -1, -1, -1, 1, -1, -1, -1, -1, -1, 5, -1, -1, 1]
                
                tempSplicePoints = [5, 9, 15] (notice, last point is excluded
                
                splicePoints = [0, 5, 9, 15, 19] 
                
                splicePoints corresponds to the boundaries of each iteration
                
         """
        
        # Find Splice Points
        subtract = numpy.zeros_like(timetags)
        subtract[0:-1] = timetags[1:len(timetags)]
        difference = timetags - subtract
        signs = numpy.sign(difference)
        tempSplicePoints = numpy.where(signs[0:-1] == 1)[0]
        splicePoints = numpy.array([0])
        splicePoints = numpy.append(splicePoints, tempSplicePoints)
        splicePoints = numpy.append(splicePoints, len(timetags))
        splicePoints = numpy.ravel(splicePoints)

        for i in range(self.expP.iterations):
            # focus on timetags for a particular iteration
            iterationTimetags = timetags[(splicePoints[i]+1):splicePoints[i + 1]]
            # If it's the first iteration, you have to include 0 (notice the '+ 1' is missing)
            if i == 0:
                iterationTimetags = timetags[splicePoints[i]:splicePoints[i + 1]]

            """ Now that a particular iteration is considered, the timetags need to be partitioned by frequency
            
                The time of readout for each frequency is known because the times are periodic and they depend on cycleTime
                
                numpy.where((iterationTimetags >= startTime) & (iterationTimetags <= stopTime))[0] -> the coordinates of the timetags that fall between the start and stop times
                
                                        ^
                The length of the above | array corresponds to the number of counts for a particular readout time.
                
                The counts are cataloged in an array (countsFreqArray) organized by frequency [counts-freq 1, counts-freq 2, counts-freq 3...]
                This way, counts can accummulate in this array over each iteration, resulting in an array that has the total number of counts for each frequency.
                
             """
                                   
            for j in range(len(freqs)):
                startTime = (cycleTime*j + start)
                stopTime = (cycleTime*j + stop)
                counts = len(numpy.where((iterationTimetags >= startTime) & (iterationTimetags <= stopTime))[0])
                countsFreqArray[j] += counts
        
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
            'cooling_freq':110.0,
            'cooling_ampl':-11.0,
            'readout_time':100.0*10**-6,
            'readout_ampl':-11.0,
            'switch_time':100.0*10**-6,
            'freq_min':90.0,
            'freq_max':130.0,
            'freq_step':1.0
            }
    exprtParams = {
        'iterations':50,
        }
    exprt = scan(params,exprtParams)
    exprt.run()