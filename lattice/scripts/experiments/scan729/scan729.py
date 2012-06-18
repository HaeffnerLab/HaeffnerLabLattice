import sys; 
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\PulseSequences')
import labrad
import numpy
import time
from scriptLibrary import dvParameters 
from PulseSequences.scan729 import scan729 as sequence
from dataProcessor import data_process

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
    
    def __init__(self, seqParams, exprtParams):
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
        
    def initialize(self):
        #directory name and initial variables
        self.dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())
        #saving
        self.dv.cd(['','Experiments', self.experimentName, self.dirappend, 'timetags'],True )
        self.dv.new('timetags',[('Freq', 'MHz')],[('Time','Sec','Sec')] )
        self.programPulser()
        self.setupLogic()
        
    def setupLogic(self):
        self.pulser.switch_auto('axial',  True) #axial needs to be inverted, so that high TTL corresponds to light ON
        self.pulser.switch_auto('110DP',  False) #high TTL corresponds to light OFF
        self.pulser.switch_auto('866DP', False) #high TTL corresponds to light OFF
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
            print 'setting frequency {} MHz'.format(freq) 
            self.synth.frequency(freq)
            self.pulser.reset_timetags()
            self.pulser.start_number(xP.iterations)
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
            timetags = self.pulser.get_timetags().asarray
            #saving timetags
            frqs = numpy.ones_like(timetags) * freq
            self.dv.add(numpy.vstack((frqs,timetags)).transpose())
    
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
        
    def __del__(self):
        self.cxn.disconnect()
    
if __name__ == '__main__':
  
    params = {
        'backgroundMeasure':1*10**-3,
        'initial_cooling':5*10**-3,
        'optical_pumping':1*10**-3,
        'rabitime':5*10**-3,
        'readout_time':10*10**-3,
        'repump854':5*10**-3,
        'repumpPower':-3.0
          }
    exprtParams = {
                   'freqMin':210.0,
                   'freqMax':230.0,
                   'freqStep':40.0,
                   'iterations':20,
                   'binTime':250.0*10**-6
                   }
    exprt = scan729(params,exprtParams)
    exprt.run()
    dp =  data_process(exprt.cxn, exprt.dirappend, ['','Experiments', exprt.experimentName, exprt.dirappend,'timetags'], ['freqscan'])
    #dp.addParameter('threshold', 13000)
    dp.loadDataVault()
    dp.processAll()