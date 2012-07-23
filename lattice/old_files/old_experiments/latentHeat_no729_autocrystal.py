import sys; sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
import labrad
import numpy
import time
from scriptLibrary.parameter import Parameters
from scriptLibrary import paulsbox 
from scriptLibrary import dvParameters 

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

#Global parameters
iterations = 10
experimentName = 'LatentHeat_no729_autocrystal'
#heating double pass frequency
axfreq = 250.0 #MHz
#110DP
cooling = (102.0, -4.9) #MHz, dBm
readout = (120.0, -4.9) 
crystallization = (102.0,-4.9)
rs110List = [cooling, readout,crystallization] 

auto_crystal = True
#paul's box parameters
pboxsequence = 'LatentHeat_no729_autocrystal.py' #all Paul's box parameters are in microseconds
initial_cooling = 75.0*10**3
heat_delay = 15.0*10**3
axial_heat = 155.0*10**3
readout_delay = 100.*10**3
readout_time = 100.*10**3

#Time Resolved Recording
recordTime = min(.55, 0.1 +  (initial_cooling + heat_delay + axial_heat + readout_delay + readout_time ) / 10.0**6)###   

globalDict = {
              'iterations':iterations,
              'experimentName':experimentName,
              'axfreq':axfreq,
              'recordTime':recordTime, 
              'cooling':cooling,
              'readout':readout,
              'crystallization':crystallization,
              }

pboxDict = {
        'sequence':pboxsequence,
        'initial_cooling':initial_cooling,
        'heat_delay':heat_delay,
        'axial_heat':axial_heat,
        'readout_delay':readout_delay,
        'readout_time':readout_time,
        }

#Binning on the fly
binTime =250.0*10**-6
binNumber = int(recordTime / binTime)
binArray = binTime * numpy.arange(binNumber + 1)
#parameters
parameters = Parameters(globalDict)
parameters.addDict(pboxDict)
#connect and define servers we'll be using
cxn = labrad.connect()
cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
dv = cxn.data_vault
dpass = cxn.double_pass
trigger = cxn.trigger
pbox = cxn.paul_box
trfpga = cxn.timeresolvedfpga
rs110DP = cxn.rohdeschwarz_server
rf = cxn.lattice_pc_hp_server

dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())

def initialize():
    trfpga.set_time_length(recordTime)
    paulsbox.program(pbox, pboxDict)
    trigger.switch_auto('axial',  False) #axial needs to be inverted, so that high TTL corresponds to light ON
    trigger.switch_auto('110DP',  True) #high TTL corresponds to light OFF
    trigger.switch_auto('866DP',  True) #high TTL corresponds to light OFF
    trigger.switch_manual('crystallization',  False) #high TTL corresponds to light OFF
    #make sure r&s synthesizers are on, and are of correct frequency
    #heating
    dpass.select('axial')
    dpass.frequency(axfreq)
    dpass.output(True)
    #readout / cooling
    dpass.select('110DP')
    dpass.output(True)
    rs110DP.select_device(dpass.device_id())
    #make sure the list is in range:
    freqRange = dpass.frequency_range()
    powerRange = dpass.amplitude_range()
    print freqRange, powerRange
    for freq,power in rs110List:
        if not (freqRange[0] <= freq <= freqRange[1]):
            raise Exception('frequency list parameters out of range')
        if not (powerRange[0] <= power <= powerRange[1]):
            raise Exception('power list parameters out of range')
    #create list and enter the list mode
    rs110DP.new_list(rs110List)
    rs110DP.activate_list_mode(True)
    rs110DP.reset_list() ####need to reset because activate list mode after programming ends up at some random step
    #repump
    dpass.select('repump')
    dpass.output(True)
    globalDict['resolution']=trfpga.get_resolution()

def sequence():
    binnedFlour = numpy.zeros(binNumber)
    for iteration in range(iterations):
        rs110DP.reset_list()
        print 'recording trace {0} out of {1}'.format(iteration+1, iterations)
        trfpga.perform_time_resolved_measurement()
        trigger.trigger('PaulBox')
        timetags = trfpga.get_result_of_measurement().asarray
        #saving timetags
        dv.cd(['','Experiments', experimentName, dirappend, 'timetags'],True )
        dv.new('timetags iter{0}'.format(iteration),[('Time', 'sec')],[('PMT counts','Arb','Arb')] )
        dv.add_parameter('iteration',iteration)
        ones = numpy.ones_like(timetags)
        dv.add(numpy.vstack((timetags,ones)).transpose())
        #add to binning of the entire sequence
        newbinned = numpy.histogram(timetags, binArray )[0]
        binnedFlour = binnedFlour + newbinned
        print 'now waiting to complete recooling'
        trigger.wait_for_pbox_completion()
        trigger.wait_for_pbox_completion() #have to call twice until bug is fixed
        if auto_crystal:
            success = auto_crystalize()
            if not success: break
    print 'getting result and adding to data vault'
    dv.cd(['','Experiments', experimentName, dirappend] )
    dv.new('binnedFlourescence',[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
    data = numpy.vstack((binArray[0:-1], binnedFlour)).transpose()
    dv.add(data)
    dv.add_parameter('plotLive',True)
    print 'gathering parameters and adding them to data vault'
    measureList = ['trapdrive','endcaps','compensation','dcoffsetonrf','cavity397','cavity866','multiplexer397','multiplexer866','axialDP']
    measuredDict = dvParameters.measureParameters(cxn, cxnlab, measureList)
    dvParameters.saveParameters(dv, measuredDict)
    dvParameters.saveParameters(dv, globalDict)
    dvParameters.saveParameters(dv, pboxDict)

def finalize():
    for name in ['axial', '110DP']:
        trigger.switch_manual(name)
    rs110DP.activate_list_mode(False)
    trigger.switch_manual('crystallization',  False)

crystal_threshold = 18 #kcounts per sec
crystallization_attempts = 10
detect_time = 0.150
far_red_time = 0.300 #seconds
optimal_cool_time = 0.150
pmtresolution = 0.025 #seconds
shutter_delay = 0.025
pmt = cxn.normalpmtflow
pmt.set_time_length(pmtresolution)
crystal_power = -5.9

def is_crystalized():
    countRate = pmt.get_next_counts('ON',int(detect_time / pmtresolution), True)
    print countRate
    print 'auto crystalization: count rate {}'.format(countRate)
    return (countRate > crystal_threshold) 
    
def auto_crystalize():
    if is_crystalized():
        print 'initially crystalized'
        return True
    else:
        print 'MELTED!!!!'
        trigger.switch_manual('crystallization',  True)
        initpower = rf.getpower()
        rf.setpower(-5.9)
        time.sleep(shutter_delay)
        for attempt in range(crystallization_attempts):
            trigger.switch_manual('110DP',  False) #turn off DP to get all light into far red 0th order
            time.sleep(far_red_time)
            trigger.switch_manual('110DP',  True) 
            time.sleep(optimal_cool_time)
            if is_crystalized():
                print 'success on attempt number {}'.format(attempt)
                trigger.switch_manual('crystallization',  False)
                time.sleep(shutter_delay)
                trigger.switch_auto('110DP',  True)
                rf.setpower(initpower)
                return True
        #if still not crystzlied, let the user handle things
        response = raw_input('Please Crystalize! Type "f" is not successful and sequence should be terminated')
        if response == 'f':
            return False
        else:
            trigger.switch_manual('crystallization',  False)
            time.sleep(shutter_delay)
            trigger.switch_auto('110DP',  True)
            rf.setpower(initpower)
            return True
            
print 'initializing measurement'
initialize()
print 'performing sequence'
sequence()
print 'finalizing'
finalize()
print 'DONE'
print dirappend