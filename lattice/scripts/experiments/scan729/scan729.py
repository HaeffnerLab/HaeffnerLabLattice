import sys; 
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\PulseSequences')
import labrad
import numpy
from scriptLibrary import dvParameters 
from PulseSequences.scan729 import scan729 as sequence
from dataProcessor import dataProcess


class scan729():
    ''''
    Performs frequency scan of 729, for each frequency calculates the probability of the ion going dark. Plots the result.
    '''
    experimentName = 'scan729'
    
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
        self.programPulser()
        self.setupLogic()
        
    def setupLogic(self):
        self.pulser.switch_auto('axial',  True) #axial needs to be inverted, so that high TTL corresponds to light ON
        self.pulser.switch_auto('110DP',  False) #high TTL corresponds to light OFF
        self.pulser.switch_auto('866DP', False) #high TTL corresponds to light OFF
        self.pulser.switch_manual('crystallization',  False) #high TTL corresponds to light OFF
    
    def programPulser(self):
        seq = sequence(self.pulser)
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
        self.pulser.switch_manual('crystallization',  True)
    
    def is_crystalized(self):
        detect_time = 0.225
        countRate = self.pmt.get_next_counts('ON',int(detect_time / self.expP.pmtresolution), True)
        print 'auto crystalization: count rate {0} and threshold is {1}'.format(countRate, self.crystal_threshold)
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
            self.rf.amplitude(rf_crystal_power)
            time.sleep(shutter_delay)
            for attempt in range(self.crystallization_attempts):
                self.pulser.switch_manual('110DP',  False) #turn off DP to get all light into far red 0th order
                time.sleep(far_red_time)
                self.pulser.switch_manual('110DP',  True) 
                time.sleep(optimal_cool_time)
                if self.is_crystalized():
                    print 'Crysallized on attempt number {}'.format(attempt + 1)
                    self.rf.amplitude(self.expP.rf_power)
                    time.sleep(rf_settling_time)
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

#connect and define servers we'll be using
cxn = labrad.connect()
cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
dv = cxn.data_vault

####rs = cxnlab.rohdeschwarz_server
rs.select_device(0)
#rf = cxn.trap_drive
pulser = cxn.pulser


#Global parameters
frequency_start= 10000  #start frequecny 
frequency_stop= 10500
frequency_step= 20   #stop frequecny 
power729 = -3.
cycles=1

frequency = numpy.linspace(frequency_start, frequency_step, frequency_stop)


rs.amplitude(power729)

experimentName = 'freqscan_experiment'

#sequence parameters
params = {
              'initial_cooling': 100e-3,
              'pump':10.0*10**-3,
              'rabitime':1.0*10**-3, ####should implement 0
              'backgroundMeasure':1.0*10**-3,
              'readout_time':10.0*10**-3,
            
            }



seq = freqscan(pulser)
pulser.new_sequence()
seq.setVariables(**params)
seq.defineSequence()
pulser.program_sequence()
recordTime = seq.parameters.recordTime

globalDict = {
              'frequency':frequency,
              'experimentName':experimentName,
              'recordTime':recordTime, 
              'cycles':cycles
              }
print 'recording for {}'.format(recordTime)

#directory name
dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())
counts = []

def sequence():
    dv.cd(['','Experiments', experimentName, dirappend, 'timetags'],True ) # goes to directory
    dv.new('timetags',[('Frequecny', 'Hz')],[('Timetags','Arb','Arb')] )
    
    #binnedFlour = numpy.zeros(binNumber)
    for iter,freq in enumerate(frequency):
        print 'recording trace {0} out of {1}'.format(iter+1, len(frequency))
        rs.frequency(freq)
          
        pulser.reset_timetags()
        pulser.start_finite(cycles)
        pulser.wait_sequence_done()
        pulser.stop_sequence()
        timetags = pulser.get_timetags().asarray
        #saving timetags
    
        for slice
         
        backgroundslice = numpy.where(timetags >  0.0 + 100e-9 , timetags < seq.backgroundMeasure)[0]
        dataslice = numpy.where(timetags >= seq.rabitempus, timetags <= seq.readtime)[0]
        coolslice = numpy.where(timetags >= seq.backgroundMeasure, timetags <= seq.inital_cool)[0]
        
        datanorm = dataslice.size/(seq.readtime-seq.rabitempus)/float(cycles)
        backgroundnorm = backgroundslice.size/(seq.backgroundMeasure)/float(cycles)
        coolnorm = coolslice.size/(seq.inital_cool-seq.backgroundMeasure)/float(cycles)
        
        if datanorm > (coolnorm-backgroundnorm)/2.0:
            count = count + 1 
        else:   
            count = count    
        count = count/float(cycles)      
        counts.append(count)
        
        freqs = freq * numpy.ones_like(timetags)   #all 1. in timetags
        dv.add(numpy.vstack((timetags,freqs)).transpose()) #combines timetags with ones


    dv.cd(['','Experiments', experimentName, dirappend] )
    dv.new('Frequency scan',[('Frequency', 'Hz')], [('Probability','Arb','Arb')] )
    data = numpy.vstack((frequency counts)).transpose()
    dv.add(data)
    dv.add_parameter('plotLive',True) #pops up window
        
    dvParameters.saveParameters(dv, globalDict)
    dvParameters.saveParameters(dv, params)

sequence()
print 'DONE'
print dirappend