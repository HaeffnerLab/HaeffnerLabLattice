import labrad
import numpy
import time
from scripts.scriptLibrary import dvParameters 
from scripts.PulseSequences.scan729_opt import scan729 as sequence

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
    
    def __setitem__(self, key, val):
        self.__dict__[key] = val
    
    def toDict(self):
        return self.__dict__
    
class scan729():
    ''''
    Performs frequency scan of 729, for each frequency calculates the probability of the ion going dark. Plots the result.
    
    Possible improvements:
        if exceeds 32K counts per iterations of cycles, be able to repeat that multiple times for a given frequency. allow for this change in data analysis
        multiple data processing, including histogram to get the threshold
    '''
    experimentName = 'scan729DDS'
    
    def __init__(self, seqParams, exprtParams, analysisParams):
        #connect and define servers we'll be using
        self.cxn = labrad.connect()
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.dv = self.cxn.data_vault
        self.pulser = self.cxn.pulser
        self.seqP = Bunch(**seqParams)
        self.expP = Bunch(**exprtParams)
        self.anaP = Bunch(**analysisParams)
        self.totalReadouts = []
        
    def initialize(self):
        #directory name and initial variables
        self.dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())
        self.directory = ['','Experiments', self.experimentName, self.dirappend]
        #saving
        self.dv.cd(self.directory ,True )
        self.dv.new('Counts',[('Freq', 'MHz')],[('Counts','Arb','Arb')] )
        self.programPulser()
        self.setupLogic()
        
    def setupLogic(self):
        self.pulser.switch_auto('axial',  True) #axial needs to be inverted, so that high TTL corresponds to light ON
        self.pulser.switch_auto('110DP',  False) #high TTL corresponds to light OFF
        self.pulser.switch_auto('866DP', False) #high TTL corresponds to light OFF
        #self.pulser.switch_auto('729DP', True)
        self.pulser.switch_manual('crystallization',  False)
    
    def programPulser(self):
        seq = sequence(self.pulser)
        self.pulser.new_sequence()
        seq.setVariables(**self.seqP.toDict())
        seq.defineSequence()
        self.pulser.program_sequence()
    
    def run(self):
        self.initialize()
        self.sequence()
        self.finalize()
        print 'DONE {}'.format(self.dirappend)
        
    def sequence(self):
        sP = self.seqP
        xP = self.expP
        for i in range(xP.iterations):
            print 'iteration {}'.format(i+1)
            self.pulser.start_number(xP.startNumber)
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
            readouts = self.pulser.get_readout_counts().asarray
            self.dv.add(numpy.vstack(((numpy.array((sP.frequencies_729)*xP.startNumber)), readouts)).transpose())       
            self.totalReadouts.append(readouts)   
    
    def finalize(self):
        #go back to inital logic
        for name in ['axial', '110DP']:
            self.pulser.switch_manual(name)
        #save information to file
        measureList = ['trapdrive','endcaps','compensation','dcoffsetonrf','cavity397','cavity866','multiplexer397','multiplexer866','axialDP', 'pulser']
        measuredDict = dvParameters.measureParameters(self.cxn, self.cxnlab, measureList)
        dvParameters.saveParameters(self.dv, measuredDict)
        dvParameters.saveParameters(self.dv, self.seqP.toDict())
        dvParameters.saveParameters(self.dv, self.expP.toDict())
        #show histogram
        self.analyze()
    
    def analyze(self):
        totalAnalyzedReadouts = numpy.zeros(len(self.seqP.frequencies_729))
        threshold = self.anaP.threshold
        totalReadouts = self.totalReadouts
        for readouts in totalReadouts:
            readouts = numpy.reshape((numpy.array(readouts < threshold, dtype=numpy.int)), (self.expP.startNumber, len(self.seqP.frequencies_729)))
            readouts = numpy.sum(readouts, axis = 0)
            totalAnalyzedReadouts += readouts
        #normalize
        totalAnalyzedReadouts /= (self.expP.iterations * self.expP.startNumber)
        #save readouts     
        self.dv.new('Spectrum Analyzed',[('Freq', 'MHz')],[('Counts','Arb','Arb')] )
        self.dv.add(numpy.vstack((self.seqP.frequencies_729,totalAnalyzedReadouts)).transpose())
        self.dv.add_parameter('Window', ['Spectrum'])
        self.dv.add_parameter('plotLive', True)
        # binning
        totalReadouts = numpy.ravel(numpy.array(totalReadouts))
        hist, bins = numpy.histogram(totalReadouts, 50)
        self.dv.new('Histogram',[('Counts', 'Arb')],[('Occurence','Arb','Arb')] )
        self.dv.add(numpy.vstack((bins[0:-1],hist)).transpose())
        self.dv.add_parameter('Histogram', self.anaP.threshold)
        
    def __del__(self):
        self.cxn.disconnect()
    
if __name__ == '__main__':
    freqs = numpy.arange(214.0, 216, 0.05)
    ampls = numpy.ones_like(freqs) * -8.0
    freqs = freqs.tolist()
    ampls = ampls.tolist()  
    params = {
                'frequencies_729':freqs,
                'amplitudes_729': ampls,
                'doppler_cooling':10*10**-3,
                'heating_time':100.0e-6,
                'rabi_time':20.0e-6,#0.5*10**-3,
                'readout_time':5*10**-3,
                'repump_time':10*10**-3,
                'repump_854_ampl': -3.0,
                'repump_866_ampl': -11.0,
                'doppler_cooling_freq':100.0,
                'doppler_cooling_ampl':-11.0,
                'readout_freq':110.0,
                'readout_ampl':-11.0,
                'optical_pump_freq':219.12,#218.47,
                'optical_pump_ampl':-63.0,#-10.0,
                'optical_pump_dur':1.0e-3
            }
    exprtParams = {
        'startNumber': 10,
        'iterations': 5,
        }
    
    analysis = {
        'threshold':18,
        }
    exprt = scan729(params,exprtParams, analysis)
    exprt.run()