import sys; 
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\PulseSequences')
import labrad
import numpy
import time
####from scriptLibrary.parameter import Parameters
from scriptLibrary import paulsbox 
from scriptLibrary import dvParameters 
from PulseSequences.latentHeat import LatentHeat
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
#connect and define servers we'll be using
cxn = labrad.connect()
cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
dv = cxn.data_vault
dpass = cxn.double_pass
rs110DP = cxn.rohdeschwarz_server
rf = cxn.trap_drive
pulser = cxn.pulser
pmt = cxn.normalpmtflow


#Global parameters
iterations = 5
experimentName = 'LatentHeat_no729_autocrystal'
axfreq = 250.0 #heating double pass frequency #MHz
#110DP
xtalFreq = 102.0
xtalPower = -4.0
cooling = (102.0, -8.0) #MHz, dBm
readout = (115.0, -8.0) 
crystallization = (xtalFreq, xtalPower)
rf_power = -3.5
rf_settling_time = 0.3
rs110List = [cooling, readout,crystallization] 
auto_crystal = True
#sequence parameters
params = {
              'initial_cooling': 100e-3,
              'heat_delay':30e-3,
              'axial_heat':75.0*10**-3,
              'readout_delay':1000.0*10**-3, ####should implement 0
              'readout_time':10.0*10**-3,
              'xtal_record':100e-3
            }
recordTime = params['initial_cooling'] + params['heat_delay'] +params['axial_heat'] + params['readout_delay'] + params['readout_time'] +  params['xtal_record']

globalDict = {
              'iterations':iterations,
              'experimentName':experimentName,
              'axfreq':axfreq,
              'recordTime':recordTime, 
              'cooling':cooling,
              'readout':readout,
              'crystallization':crystallization,
              'rf_power':rf_power,
              'rf_settling_time':rf_settling_time
              }

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
dpass.select('110DP')
dpass.frequency(xtalFreq)
dpass.amplitude(xtalPower)
countRate = pmt.get_next_counts('ON',int(detect_time / pmtresolution), True)
print 'initial countrate', countRate
crystal_threshold = 0.8 * countRate #kcounts per sec
crystallization_attempts = 10
print 'Crystallization threshold: ', crystal_threshold


def initialize():
    #pmt recording
    pmt.set_time_length(pmtresolution)
    #pulser sequence 
    seq = LatentHeat(pulser)
    pulser.new_sequence()
    seq.setVariables(**params)
    seq.defineSequence()
    pulser.program_sequence()
    pulser.switch_auto('axial',  True) #axial needs to be inverted, so that high TTL corresponds to light ON
    pulser.switch_auto('110DP',  False) #high TTL corresponds to light OFF
    pulser.switch_auto('866DP', False) #high TTL corresponds to light OFF
    pulser.switch_auto('110DPlist', False) #high TTL corresponds to light OFF
    pulser.switch_manual('crystallization',  False) #high TTL corresponds to light OFF
    #make sure r&s synthesizers are on, and are of correct frequency
    #heating
####    dpass.select('axial')
####    dpass.frequency(axfreq)
####    dpass.output(True)
    #readout / cooling
####    dpass.select('110DP')
####    dpass.output(True)
    rs110DP.select_device(dpass.device_id())
    #make sure the list is in range:
    freqRange = dpass.frequency_range()
    powerRange = dpass.amplitude_range()
    for freq,power in rs110List:
        if not (freqRange[0] <= freq <= freqRange[1]):
            raise Exception('frequency list parameters out of range')
        if not (powerRange[0] <= power <= powerRange[1]):
            raise Exception('power list parameters out of range')
    #create list and enter the list mode
    rs110DP.new_list(rs110List)
    rs110DP.activate_list_mode(True)
    time.sleep(0.50) #letting list mode activate

def sequence():
    binnedFlour = numpy.zeros(binNumber)
    for iteration in range(iterations):
        print 'recording trace {0} out of {1}'.format(iteration+1, iterations)
        rs110DP.reset_list()
        pulser.reset_timetags()
        pulser.start_single()
        pulser.wait_sequence_done()
        pulser.stop_sequence()
        timetags = pulser.get_timetags().asarray
        #saving timetags
        dv.cd(['','Experiments', experimentName, dirappend, 'timetags'],True )
        dv.new('timetags iter{0}'.format(iteration),[('Time', 'sec')],[('PMT counts','Arb','Arb')] )
        dv.add_parameter('iteration',iteration)
        ones = numpy.ones_like(timetags)
        dv.add(numpy.vstack((timetags,ones)).transpose())
        #add to binning of the entire sequence
        newbinned = numpy.histogram(timetags, binArray )[0]
        binnedFlour = binnedFlour + newbinned
        if auto_crystal:
            success = auto_crystalize()
            if not success: break
    # getting result and adding to data vault
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
    rs110DP.activate_list_mode(False)
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
        #if still not crystzlied, let the user handle things
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