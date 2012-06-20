import sys; 
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\PulseSequences')
import labrad
import numpy
import time
from scriptLibrary import dvParameters 
from PulseSequences.scan729 import scan729 as sequence
from dataProcessor import freqscan

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
    experimentName = 'scan729'
    
    def __init__(self, seqParams, exprtParams, analysisParams):
       #connect and define servers we'll be using
        self.cxn = labrad.connect()
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.synth = self.cxnlab.rohdeschwarz_server
        self.synth.select_device('lab-49 GPIB Bus - USB0::0x0AAD::0x0054::104542')
        self.initfreq = self.synth.frequency()
        self.dv = self.cxn.data_vault
        self.pulser = self.cxn.pulser
        self.seqP = Bunch(**seqParams)
        self.expP = Bunch(**exprtParams)
        self.anaP = Bunch(**analysisParams)
        
    def initialize(self):
        #directory name and initial variables
        self.dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())
        self.directory = ['','Experiments', self.experimentName, self.dirappend]
        #saving
        self.dv.cd(self.directory ,True )
        self.dv.new('timetags',[('Freq', 'MHz')],[('Time','Sec','Sec')] )
        self.programPulser()
        self.setupLogic()
        self.setupAnalysis()
        
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
        self.seqP['recordTime'] = seq.recordTime
        self.seqP['startReadout'] = seq.startReadout
        self.seqP['stopReadout'] = seq.stopReadout
    
    def setupAnalysis(self):
        self.dp = freqscan(self.seqP.startReadout, self.seqP.stopReadout, self.dv, self.directory, threshold = self.anaP.threshold)
    
    def run(self):
        sP = self.seqP
        xP = self.expP
        self.initialize()
        self.sequence()
        self.finalize()
        print 'DONE {}'.format(self.dirappend)
        
    def sequence(self):
        sP = self.seqP
        xP = self.expP
        frequencies = numpy.arange(xP.freqMin, xP.freqMax + xP.freqStep, xP.freqStep)
        frequencies = frequencies[((frequencies >= xP.freqMin) * (frequencies <= xP.freqMax))] #prevents issues when step size > (max - min)
        for freq in frequencies:
            self.synth.frequency(freq)
            self.pulser.reset_timetags()
            self.pulser.start_number(xP.iterations)
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
            timetags = self.pulser.get_timetags().asarray
            print 'frequency {} : got {} timetags'.format(freq, timetags.size)
            #saving timetags
            frqs = numpy.ones_like(timetags) * freq
            self.dv.add(numpy.vstack((frqs,timetags)).transpose())
            self.dp.addFrequency(freq, timetags, addToPlot = True)
    
    def finalize(self):
        #go back to initiali frequency
        self.synth.frequency(self.initfreq)
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
        self.dp.makeHistPlot()
        
    def __del__(self):
        self.cxn.disconnect()
    
if __name__ == '__main__':
  
    params = {
        'coolingFreq397':110.0,
        'coolingPower397':-19.0,
        'readoutFreq397':110.0,
        'readoutPower397':-11.0,
        'backgroundMeasure':1*10**-3,
        'initial_cooling':5*10**-3,
        'optical_pumping':1*10**-3,
        'rabitime':5*10**-6,
        'readout_time':20*10**-3,
        'repump854':5*10**-3,
        'repumpPower':-3.0
          }
    exprtParams = {
        'freqMin':216.069,
        'freqMax':216.071,
        'freqStep':0.000002,
        'iterations':75,
        }
    
    analysis = {
        'threshold':170,
        }
    exprt = scan729(params,exprtParams, analysis)
    exprt.run()