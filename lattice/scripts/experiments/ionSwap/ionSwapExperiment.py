import sys; 
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\PulseSequences')
sys.path.append('/home/lattice/Desktop/LabRAD/lattice/scripts')
sys.path.append('/home/lattice/Desktop/LabRAD/lattice/PulseSequences')
import labrad
import numpy
import time
####from scriptLibrary.parameter import Parameters
from scriptLibrary import dvParameters 
from PulseSequences.ionSwap import IonSwapBackground
from dataProcessor_ionSwap import data_process
''''
This experiment examines the probability of ions swapping places during heating. 
After all cooling lights are switched off, the crystal is heated with far blue light for a variable time. Readout is meant to be done with a near resonant light.
Typically vary:
    axial_heat
    heating delay
Features:
    729nm used to tag one of the ions to detect position swapping. 854nm used to rebrigthen all the ions.
    866 is switched off together with 397 to prevent cooling when it's not intended
    automatic crystallization routine to reduce necessary time to crystallize the ions

'''
#connect and define servers we'll be using
cxn = labrad.connect()
cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
dv = cxn.data_vault
#dpass = cxn.double_pass
#rs110DP = cxn.rohdeschwarz_server
rf = cxn.trap_drive
pulser = cxn.pulser
pmt = cxn.normalpmtflow

#Global parameters
iterations = 100
experimentName = 'IonSwap'
#axfreq = 250.0 #heating double pass frequency #MHz
#110DP
xtalFreq397 = 103.0
xtalPower397 = -11.0 
xtalPower866 = -3.0
#cooling = (103.0, -8.0) #MHz, dBm
#readout = (115.0, -8.0) 
rf_power = -3.5
rf_settling_time = 0.3
#rs110List = [cooling, readout,crystallization] 
auto_crystal = True
#sequence parameters
params = { 
          'exposure': 100*10**-3,
          'camera_delay': 20*10**-3, 
          'initial_cooling': 65*10**-3, #includes delay 15ms delay after background collection
          'darkening': 100*10**-3,
          'heat_delay':5*10**-3,
          'axial_heat':9*10**-3,
          'readout_delay':100*10**-9,
          'readout_time':10*10**-3,
          'rextal_time': 25*10**-3,
          'brightening': 5*10**-3,
          'cooling_ampl_866':-15.0,
          'readout_ampl_866':-11.0,
          'xtal_ampl_866':xtalPower866,
          'cooling_freq_397':103.0,
          'cooling_ampl_397':-13.0,
          'readout_freq_397':115.0,
          'readout_ampl_397':-15.0,
          'xtal_freq_397':xtalFreq397,
          'xtal_ampl_397':xtalPower397,
          }
seq = IonSwapBackground(pulser)
pulser.new_sequence()
seq.setVariables(**params)
seq.defineSequence()
pulser.program_sequence()
recordTime = seq.parameters.recordTime

globalDict = {
              'iterations':iterations,
              'experimentName':experimentName,
              'recordTime':recordTime, 
              'rf_power':rf_power,
              'rf_settling_time':rf_settling_time
              }
print 'recording for {}'.format(recordTime)

#Binning on the fly
binTime =250.0*10**-6
binNumber = int(recordTime / binTime)
binArray = binTime * numpy.arange(binNumber + 1)
#directory name
dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())
#auto-crystallization settings
meltedTimes = 0
detect_time = 0.225
far_red_time = 0.300 #seconds
optimal_cool_time = 0.150
pmtresolution = 0.075 #seconds 
shutter_delay = 0.025
rf_crystal_power = -7.0
pulser.select_dds_channel('110DP')
pulser.frequency(xtalFreq397)
pulser.amplitude(xtalPower397)
pulser.select_dds_channel('866DP')
pulser.amplitude(xtalPower866)
countRate = pmt.get_next_counts('ON',int(detect_time / pmtresolution), True)
print 'initial countrate', countRate
crystal_threshold = 0.7 * countRate #kcounts per sec #changes from .8 4/19
crystallization_attempts = 10
print 'Crystallization threshold: ', crystal_threshold


def initialize():
    #pmt recording
    pmt.set_time_length(pmtresolution)
    #pulser sequence 
    pulser.switch_auto('axial',  True) #axial needs to be inverted, so that high TTL corresponds to light ON
    pulser.switch_auto('110DP',  False) #high TTL corresponds to light OFF
    pulser.switch_auto('866DP', False) #high TTL corresponds to light OFF
#    pulser.switch_auto('110DPlist', False) #high TTL corresponds to light OFF
    pulser.switch_manual('crystallization',  False) #high TTL corresponds to light OFF

    dv.cd(['','Experiments', experimentName, dirappend, 'timetags'],True )
    dv.new('timetags',[('Time', 'sec')],[('PMT counts','Arb','Arb')] )
    dv.add_parameter('totalIterations',iterations)

    
def sequence():
    binnedFlour = numpy.zeros(binNumber)
    for iteration in range(iterations):
        print 'recording trace {0} out of {1}'.format(iteration+1, iterations)
        pulser.reset_timetags()
        pulser.start_single()
        pulser.wait_sequence_done()
        pulser.stop_sequence()
        timetags = pulser.get_timetags().asarray
        #saving timetags
        ones = numpy.ones_like(timetags)
        ones.fill(iteration)
        dv.add(numpy.vstack((timetags,ones)).transpose())
        
        #add to binning of the entire sequence
        newbinned = numpy.histogram(timetags, binArray )[0]
        binnedFlour = binnedFlour + newbinned
        if auto_crystal:
            success = auto_crystalize()
            if not success: break
    # getting result and adding to data vault
    binnedFlour = binnedFlour / float(iterations)
    binnedFlour = binnedFlour / binTime
    dv.cd(['','Experiments', experimentName, dirappend] )
    dv.new('binnedFlourescence',[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
    data = numpy.vstack((binArray[0:-1], binnedFlour)).transpose()
    dv.add(data)
    dv.add_parameter('plotLive',True)
    # gathering parameters and adding them to data vault
    measureList = ['trapdrive','endcaps','compensation','dcoffsetonrf','cavity397','cavity866','multiplexer397','multiplexer866','axialDP', 'pulser']
    measuredDict = dvParameters.measureParameters(cxn, cxnlab, measureList)
    dvParameters.saveParameters(dv, measuredDict)
    dvParameters.saveParameters(dv, globalDict)
    dvParameters.saveParameters(dv, params)

def finalize():
    for name in ['axial', '110DP']:
        pulser.switch_manual(name)
#    rs110DP.activate_list_mode(False)
    pulser.switch_manual('crystallization',  True)

def is_crystalized():
    countRate = pmt.get_next_counts('ON',int(detect_time / pmtresolution), True)
    print 'auto crystalization: count rate {0} and threshold is {1}'.format(countRate, crystal_threshold)
    return (countRate > crystal_threshold) 
    
def auto_crystalize():
    global meltedTimes
    if is_crystalized():
        print 'Crystallized'
        return True
    else:
        print 'Melted'
        meltedTimes += 1
        pulser.switch_manual('crystallization',  True)
        initpower = rf.amplitude()
        rf.amplitude(rf_crystal_power)
        time.sleep(shutter_delay)
        for attempt in range(crystallization_attempts):
            pulser.switch_manual('110DP',  False) #turn off DP to get all light into far red 0th order
            time.sleep(far_red_time)
            pulser.switch_manual('110DP',  True) 
            time.sleep(optimal_cool_time)
            if is_crystalized():
                print 'Crysallized on attempt number {}'.format(attempt + 1)
                rf.amplitude(rf_power)
                time.sleep(rf_settling_time)
                pulser.switch_manual('crystallization',  False)
                time.sleep(shutter_delay)
                pulser.switch_auto('110DP',  False)
                return True
        #if still not crystallized, let the user handle things
        response = raw_input('Please Crystalize! Type "f" is not successful and sequence should be terminated')
        if response == 'f':
            return False
        else:
            rf.amplitude(initpower)
            time.sleep(rf_settling_time)
            pulser.switch_manual('crystallization',  False)
            time.sleep(shutter_delay)
            pulser.switch_auto('110DP',  False)
            return True
            
print 'initializing measurement'
initpower = rf.amplitude()
rf.amplitude(rf_power)
print rf.amplitude()
time.sleep(rf_settling_time)
initialize()
print 'performing sequence'
sequence()
print 'finalizing'
finalize()
rf.amplitude(initpower)
print 'DONE'
print dirappend
print 'melted {0} times'.format(meltedTimes)
dp =  data_process(cxn, dirappend, ['','Experiments', experimentName], ['histogram'])
dp.addParameter('threshold', 200)
dp.addParameter('startReadout', seq.parameters.startReadout)
dp.addParameter('stopReadout', seq.parameters.stopReadout)
dp.addParameter('iterations', iterations)
dp.loadDataVault()
dp.processAll()