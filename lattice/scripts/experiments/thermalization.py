import sys; 
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\PulseSequences')
import labrad
import numpy
import time
from scriptLibrary import paulsbox 
from scriptLibrary import dvParameters 
from PulseSequences.thermalization import thermalization
''''
This experiment studies how the ion heats up. After initial cooling it is repeatedly interrogated with an on resonance beam.
'''
#connect and define servers we'll be using
cxn = labrad.connect()
cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
dv = cxn.data_vault
dpass = cxn.double_pass
rs110DP = cxn.rohdeschwarz_server
rf = cxn.lattice_pc_hp_server
pulser = cxn.pulser


#Global parameters
iterations = 100
experimentName = 'thermalization'
axfreq = 220.0 #heating double pass frequency #MHz
auto_crystal = False #typical RF drive not connected
#sequence parameters
params = {
          'initial_cooling': 20e-3,
          'probe_number':100,
          'probe_off':10e-3,
          'probe_on':1e-3,
              }

recordTime = params['initial_cooling'] + params['probe_number']  * (params['probe_off'] + params['probe_on'])

globalDict = {
              'iterations':iterations,
              'experimentName':experimentName,
              'recordTime':recordTime, 
              }

#Binning on the fly
binTime =250.0*10**-6
binNumber = int(recordTime / binTime)
binArray = binTime * numpy.arange(binNumber + 1)
#directory name
dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())

def initialize():
    seq = thermalization(pulser)
    pulser.new_sequence()
    seq.setVariables(**params)
    seq.defineSequence()
    pulser.program_sequence()
    pulser.switch_auto('axial',  True) #axial needs to be inverted, so that high TTL corresponds to light ON
    pulser.switch_auto('110DP',  True) #high TTL corresponds to light ON
    #make sure r&s synthesizers are on, and are of correct frequency
    #heating
    dpass.select('axial')
    dpass.frequency(axfreq)
    dpass.output(True)
    #readout / cooling
    dpass.select('110DP')
    dpass.output(True)
    #make sure the list is in range:
    globalDict['resolution']=pulser.get_timetag_resolution()

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
    dvParameters.saveParameters(dv, params)

def finalize():
    for name in ['axial', '110DP']:
        pulser.switch_manual(name)
    rs110DP.activate_list_mode(False)
    pulser.switch_manual('crystallization',  True)

    
detect_time = 0.150
far_red_time = 0.300 #seconds
optimal_cool_time = 0.150
pmtresolution = 0.025 #seconds 
shutter_delay = 0.025
pmt = cxn.normalpmtflow
pmt.set_time_length(pmtresolution) 
crystal_power = -5.9
countRate = pmt.get_next_counts('ON',int(detect_time / pmtresolution), True)
print 'initial countrate', countRate
crystal_threshold = 0.6 * countRate #kcounts per sec
print 'Crystallization threshold: ', crystal_threshold

def is_crystalized():
    countRate = pmt.get_next_counts('ON',int(detect_time / pmtresolution), True)
    #temp = pulser.get_timetags().asarray   # work around to dump the data
    print 'auto crystalization: count rate {}'.format(countRate)
    return (countRate > crystal_threshold) 
    
def auto_crystalize():
    if is_crystalized():
        print 'initially crystalized'
        return True
    else:
        print 'MELTED!!!!'
        pulser.switch_manual('crystallization',  True)
        initpower = rf.getpower()
        rf.setpower(-5.9)
        time.sleep(shutter_delay)
        for attempt in range(crystallization_attempts):
            pulser.switch_manual('110DP',  False) #turn off DP to get all light into far red 0th order
            time.sleep(far_red_time)
            pulser.switch_manual('110DP',  True) 
            time.sleep(optimal_cool_time)
            if is_crystalized():
                print 'success on attempt number {}'.format(attempt)
                rf.setpower(initpower)
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
            rf.setpower(initpower)
            time.sleep(rf_settling_time)
            pulser.switch_manual('crystallization',  False)
            time.sleep(shutter_delay)
            pulser.switch_auto('110DP',  False)
            return True
            
print 'initializing measurement'
#initpower = rf.getpower()
#rf.setpower(rf_power)
#time.sleep(rf_settling_time)
initialize()
print 'performing sequence'
sequence()
print 'finalizing'
finalize()
#rf.setpower(initpower)
print 'DONE'
print dirappend