import sys; 
sys.path.append('/home/lattice/LabRAD/lattice/scripts')
sys.path.append('/home/lattice/LabRAD/lattice/PulseSequences')
import labrad
from labrad import types as T
import numpy
import time
from scriptLibrary import dvParameters 
from PulseSequences.latentHeat import LatentHeatBackground
from crystallizer import Crystallizer
from frequencycorrector import FrequencyCorrector
from fly_processing import Binner, Splicer

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
    
    def __setitem__(self, key, val):
        self.__dict__[key] = val
    
    def toDict(self):
        return self.__dict__

class LatentHeat():
    ''''
    This experiment involves studying the sharpness of crystal to cloud phase transition. 
    After all cooling lights are switched off, the crystal is heated with far blue light for a variable time. Readout is meant to be done with a near resonant light.
    Typically vary:
        axial_heat
        heating delay
    Features:
        independent control of hearing duration and waiting time afterwards
        866 is switched off together with 397 to prevent cooling when it's not intended
        automatic crystallization routine to reduce necessary time to crystallize the ions
        frequency switching during the sequence with the RS list mode
    '''
    experimentName = 'LatentHeat_Auto'
    
    def __init__(self, seqParams, exprtParams):
        #connect and define servers we'll be using
        self.cxn = labrad.connect()
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.dv = self.cxn.data_vault
        self.rf = self.cxn.trap_drive
        self.pulser = self.cxn.pulser
        self.pmt = self.cxn.normalpmtflow
        self.laserdac = self.cxn.laserdac
        self.seqP = Bunch(**seqParams)
        self.expP = Bunch(**exprtParams)
        self.xtal = Crystallizer(self.pulser, self.pmt, self.rf)
        self.freqCorrect = FrequencyCorrector(self.pmt, self.laserdac)
        self.Binner = None
        
    def initialize(self):
        #get initialize count for crystallization
        self.xtal.get_initial_rate()
        #get initial count for frequency correction
        self.freqCorrect.get_initial_rate()
        #directory name and initial variables
        self.dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())
        self.topdirectory = time.strftime("%Y%b%d",time.localtime())
        self.setupLogic()
        #get the count rate for the crystal at the same parameters as crystallization
        self.pulser.select_dds_channel('110DP')
        self.pulser.frequency(T.Value(self.seqP.xtal_freq_397, 'MHz'))
        self.pulser.amplitude(T.Value(self.seqP.xtal_ampl_397, 'dBm'))
        self.pulser.select_dds_channel('866DP')
        self.pulser.amplitude(T.Value(self.seqP.xtal_ampl_866,'dBm'))
        self.programPulser()
        #data processing setup
        self.Binner = Binner(self.seqP.recordTime, self.expP.binTime)
        self.Splicer = Splicer(self.seqP.startReadout, self.seqP.endReadout)
        
    def setupLogic(self):
        self.pulser.switch_auto('axial',  True) #axial needs to be inverted, so that high TTL corresponds to light ON
        self.pulser.switch_auto('110DP',  False) #high TTL corresponds to light OFF
        self.pulser.switch_auto('866DP', False) #high TTL corresponds to light OFF
        self.pulser.switch_manual('crystallization',  False)
    
    def programPulser(self):
        seq = LatentHeatBackground(self.pulser)
        self.pulser.new_sequence()
        seq.setVariables(**self.seqP.toDict())
        seq.defineSequence()
        self.pulser.program_sequence()
        self.seqP['recordTime'] = seq.parameters.recordTime
        self.seqP['startReadout'] = seq.parameters.startReadout
        self.seqP['endReadout'] = seq.parameters.endReadout
    
    def run(self):
        sP = self.seqP
        xP = self.expP
        initpower = self.rf.amplitude()
        self.rf.amplitude(xP.rf_power)
        time.sleep(xP.rf_settling_time)
        self.initialize()
        self.sequence()
        self.finalize()
        self.rf.amplitude(initpower)
        print 'DONE {}'.format(self.dirappend)

    def sequence(self):
        sP = self.seqP
        xP = self.expP
        #saving timetags
        self.dv.cd(['','Experiments', self.experimentName, self.topdirectory, self.dirappend], True)
        self.dv.new('timetags',[('Time', 'sec')],[('PMT counts','Arb','Arb')] )
        #do iterations
        for iteration in range(xP.iterations):
            print 'recording trace {0} out of {1}'.format(iteration+1, xP.iterations)
            self.pulser.reset_timetags()
            self.pulser.start_single()
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
            timetags = self.pulser.get_timetags().asarray
            iters = iteration * numpy.ones_like(timetags) 
            self.dv.add(numpy.vstack((iters,timetags)).transpose())
            #add to binning of the entire sequence
            self.Binner.add(timetags)
            self.Splicer.add(timetags)
            #auto crystallization
            if xP.auto_crystal:
                success = self.xtal.auto_crystallize()
                if not success: break
            #auto frequency correct
            if xP.freq_correct:
                if (xP.iterations % xP.freq_correct_interval == 0):
                    success = self.freqCorrect.auto_correct()
                    if not success: print 'Cant the drift, Boss'
            
        #adding readout counts to data vault:
        readout = self.Splicer.getList()
        self.dv.cd(['','Experiments', self.experimentName, self.topdirectory, self.dirappend])
        self.dv.new('readout',[('Iter', 'Number')], [('PMT counts','Counts/Sec','Counts/Sec')] )
        self.dv.add(readout)
        #adding binned fluorescence to data vault:
        binX, binY = self.Binner.getBinned()
        self.dv.cd(['','Experiments', self.experimentName, self.topdirectory, self.dirappend])
        self.dv.new('binned',[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
        data = numpy.vstack((binX, binY)).transpose()
        self.dv.add(data)
        self.dv.add_parameter('Window',['Binned Fluorescence'])
        self.dv.add_parameter('plotLive',True)
        #adding histogram of counts to data vault
        binX, binY = self.Splicer.getHistogram()
        self.dv.cd(['','Experiments', self.experimentName, self.topdirectory, self.dirappend])
        self.dv.new('histogram',[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
        data = numpy.vstack((binX, binY)).transpose()
        self.dv.add(data)
        self.dv.add_parameter('Window',['Histogram'])
        self.dv.add_parameter('plotLive',True)
        # gathering parameters and adding them to data vault
        measureList = ['trapdrive','endcaps','compensation','dcoffsetonrf','cavity397','cavity866','multiplexer397','multiplexer866','axialDP', 'pulser']
        measuredDict = dvParameters.measureParameters(self.cxn, self.cxnlab, measureList)
        dvParameters.saveParameters(self.dv, measuredDict)
        dvParameters.saveParameters(self.dv, sP.toDict())
        dvParameters.saveParameters(self.dv, xP.toDict())
    
    def finalize(self):
        for name in ['axial', '110DP']:
            self.pulser.switch_manual(name)
        below, above = self.Splicer.getPercentage(self.expP.threshold)
        print '{0:.1f}% of samples are Melted, below threshold of {1} '.format(100 * below, self.expP.threshold)
        print '{0:.1f}% of samples are Crystallized, above threshold of {1} '.format(100 * above, self.expP.threshold)
    
    def __del__(self):
        self.cxn.disconnect()
        
if __name__ == '__main__':
    #experiment parameters
    params = {
        'initial_cooling': 25e-3,
        'heat_delay':10e-3,###DO NOT CHANGE
        'axial_heat':10.9*10**-3,
        'readout_delay':100.0*10**-9,
        'readout_time':10.0*10**-3,
        'xtal_record':100e-3,
        'cooling_ampl_866':-11.0,
        'heating_ampl_866':-11.0,
        'readout_ampl_866':-11.0,
        'xtal_ampl_866':-11.0,
        'cooling_freq_397':103.0,
        'cooling_ampl_397':-13.5,
        'readout_freq_397':115.0,
        'readout_ampl_397':-13.5,
        'xtal_freq_397':103.0,
        'xtal_ampl_397':-11.0,
    }
    exprtParams = {
       'iterations':25, 
       'rf_power': T.Value(-3.5,'dBm'), #### make optional
       'rf_settling_time':0.3,
       'auto_crystal':True,
       'pmtresolution':0.075,
       'detect_time':0.225,
       'binTime':250.0*10**-6,
       'threshold':35000,
       'freq_correct':True,
       'freq_correct_interval': 5
    }
    exprt = LatentHeat(params,exprtParams)
    exprt.run()