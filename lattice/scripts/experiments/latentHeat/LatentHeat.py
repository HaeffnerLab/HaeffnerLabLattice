import sys; 
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\PulseSequences')
import labrad
import numpy
import time
from scriptLibrary import dvParameters 
from PulseSequences.latentHeat import LatentHeatBackground
from dataProcessor import data_process

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
    
    def __setitem__(self, key, val):
        self.__dict__[key] = val
    
    def toDict(self):
        return self.__dict__
        
class Crystalizer():
    pass

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
    experimentName = 'LatentHeat_no729_autocrystal'
    
    def __init__(self, seqParams, exprtParams):
       #connect and define servers we'll be using
        self.cxn = labrad.connect()
        self.cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
        self.dv = self.cxn.data_vault
        self.rf = self.cxn.trap_drive
        self.pulser = self.cxn.pulser
        self.pmt = self.cxn.normalpmtflow
        self.seqP = Bunch(**seqParams)
        self.expP = Bunch(**exprtParams)
        
    def initialize(self):
        #directory name and initial variables
        self.meltedTimes = 0
        self.dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())
        self.pmt.set_time_length(self.expP.pmtresolution)
  
        self.setupLogic()
        ###this goes to xtalizer
        #get the count rate for the crystal at the same parameters as crystallization
        self.pulser.select_dds_channel('110DP')
        self.pulser.frequency(self.seqP.xtal_freq_397)
        self.pulser.amplitude(self.seqP.xtal_ampl_397)
        self.pulser.select_dds_channel('866DP')
        self.pulser.amplitude(self.seqP.xtal_ampl_866)
        self.programPulser()
        countRate = self.pmt.get_next_counts('ON',int(self.expP.detect_time / self.expP.pmtresolution), True)
        self.crystal_threshold = 0.9 * countRate #kcounts per sec
        self.crystallization_attempts = 10
        print 'initial countrate', countRate
        print 'Crystallization threshold: ', self.crystal_threshold
        
    def setupLogic(self):
        self.pulser.switch_auto('axial',  True) #axial needs to be inverted, so that high TTL corresponds to light ON
        self.pulser.switch_auto('110DP',  False) #high TTL corresponds to light OFF
        self.pulser.switch_auto('866DP', False) #high TTL corresponds to light OFF
        self.pulser.switch_manual('crystallization',  False) #high TTL corresponds to light OFF
    
    def programPulser(self):
        seq = LatentHeatBackground(self.pulser)
        self.pulser.new_sequence()
        seq.setVariables(**params)
        seq.defineSequence()
        self.pulser.program_sequence()
        self.seqP['recordTime'] = seq.parameters.recordTime
    
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
        print 'had to recrystallize {0} times'.format(self.meltedTimes)
        
    def sequence(self):
        sP = self.seqP
        xP = self.expP
        #binning on the fly
        binNumber = int(sP.recordTime / xP.binTime)
        binArray = xP.binTime * numpy.arange(binNumber + 1)
        binnedFlour = numpy.zeros(binNumber)
        #do iterations
        for iteration in range(xP.iterations):
            print 'recording trace {0} out of {1}'.format(iteration+1, xP.iterations)
            self.pulser.reset_timetags()
            self.pulser.start_single()
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
            timetags = self.pulser.get_timetags().asarray
            #saving timetags
            self.dv.cd(['','Experiments', self.experimentName, self.dirappend, 'timetags'],True )
            self.dv.new('timetags iter{0}'.format(iteration),[('Time', 'sec')],[('PMT counts','Arb','Arb')] )
            self.dv.add_parameter('iteration',iteration)
            ones = numpy.ones_like(timetags)
            self.dv.add(numpy.vstack((timetags,ones)).transpose())
            #add to binning of the entire sequence
            newbinned = numpy.histogram(timetags, binArray )[0]
            binnedFlour = binnedFlour + newbinned
            if xP.auto_crystal:
                success = self.auto_crystalize()
                if not success: break
        # getting result and adding to data vault
        #normalize
        binnedFlour = binnedFlour / float(xP.iterations)
        binnedFlour = binnedFlour / xP.binTime
        self.dv.cd(['','Experiments', self.experimentName, self.dirappend] )
        self.dv.new('binnedFlourescence',[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
        data = numpy.vstack((binArray[0:-1], binnedFlour)).transpose()
        self.dv.add(data)
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
    
    def is_crystalized(self):
        detect_time = 0.225
        countRate = self.pmt.get_next_counts('ON',int(detect_time / self.expP.pmtresolution), True)
        print 'auto crystalization: count rate {0:.2f} and threshold is {1:.2f}'.format(countRate, self.crystal_threshold)
        return (countRate > self.crystal_threshold) 
    
    def auto_crystalize(self):
        #auto-crystallization settings###
        far_red_time = 0.300 #seconds
        optimal_cool_time = 0.150
        shutter_delay = 0.025
        rf_crystal_power = -7.0
        rf_settling_time = 0.3
        if self.is_crystalized():
            print 'Crystallized at the end'
            return True
        else:
            print 'Melted'
            self.meltedTimes += 1
            self.pulser.switch_manual('crystallization',  True)
            initpower = self.rf.amplitude()
            for attempt in range(self.crystallization_attempts):
                self.rf.amplitude(rf_crystal_power)
                time.sleep(rf_settling_time)
                time.sleep(shutter_delay)
                self.pulser.switch_manual('110DP',  False) #turn off DP to get all light into far red 0th order
                time.sleep(far_red_time)
                self.pulser.switch_manual('110DP',  True) 
                time.sleep(optimal_cool_time)
                self.rf.amplitude(self.expP.rf_power)
                time.sleep(rf_settling_time)
                if self.is_crystalized():
                    print 'Crystalized on attempt number {}'.format(attempt + 1)                    
                    self.pulser.switch_manual('crystallization',  False)
                    time.sleep(shutter_delay)
                    self.pulser.switch_auto('110DP',  False)
                    return True
            #if still not crystallized, let the user handle things
            response = raw_input('Please Crystalize! Type "f" is not successful and sequence should be terminated')
            if response == 'f':
                return False
            else:
                self.rf.amplitude(initpower)
                time.sleep(self.expP.rf_settling_time)
                self.pulser.switch_manual('crystallization',  False)
                time.sleep(shutter_delay)
                self.pulser.switch_auto('110DP',  False)
                return True
    
    def __del__(self):
        self.cxn.disconnect()
        
if __name__ == '__main__':
    #experiment parameters
    for i in range(1):
        params = {
              'initial_cooling': 25e-3,
              'heat_delay':10e-3,###DO NOT CHANGE
              'axial_heat':10.9*10**-3,
              'readout_delay':2000.0*10**-3,
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
                       'iterations':200,
                       'rf_power':-3.5, #### make optional
                       'rf_settling_time':0.3,
                       'auto_crystal':True,
                       'pmtresolution':0.075,
                       'detect_time':0.225,
                       'binTime':250.0*10**-6
                       }
        exprt = LatentHeat(params,exprtParams)
        exprt.run()
        dp =  data_process(exprt.cxn, exprt.dirappend, ['','Experiments', exprt.experimentName], ['histogram'])
        dp.addParameter('threshold', 35000)
        dp.loadDataVault()
        dp.processAll()