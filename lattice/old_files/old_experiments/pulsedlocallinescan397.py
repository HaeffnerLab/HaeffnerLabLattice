import sys; sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
import labrad
import numpy
import time
from scriptLibrary import registry
from scriptLibrary.parameter import Parameters
from scriptLibrary import paulsbox 
from scriptLibrary import dvParameters 

##Frequency Scan of Local Heating Beam
"""performing line scan with repeated pulses and heating and cooling"""
experimentName = 'PulsedLocalLineScan'
comment = 'no comment'
NUM_STEP_FREQ = 10
MIN_FREQ = 210.0 #MHZ
MAX_FREQ = 250.0 #MHZ
scanList = numpy.r_[MIN_FREQ:MAX_FREQ:complex(0,NUM_STEP_FREQ)]
##Timing for Paul's Box Sequence, all in microseconds
pboxSequence = 'PulsedLocalLineScan.py' 
number_of_pulses = 200.0
shutter_delay_time = 20.*10**3 #microseconds
heat_cool_delay = 100.0#microseconds
radial_heating_time = 1.*10**3 #microseconds
cooling_ax_time = 1.*10**3 #microseconds
iterationsPerFreq = 5#how many traces to take at each frequency
##timing for time resolved recording
recordTime =  (shutter_delay_time + number_of_pulses * (2 * heat_cool_delay + radial_heating_time + cooling_ax_time)) / 10**6 #in seconds
#data processing on the fly
binTime =50.0*10**-6
binNumber = int(recordTime / binTime)
binArray = binTime * numpy.arange(binNumber + 1)
heatCountsArray = numpy.zeros_like(scanList)
coolCountsArray = numpy.zeros_like(scanList)
#connect connect and define servers we'll be using
cxn = labrad.connect()
dv = cxn.data_vault
dpass = cxn.double_pass
trigger = cxn.trigger
pbox = cxn.paul_box
trfpga = cxn.timeresolvedfpga
dp = cxn.dataprocessor
reg = cxn.registry
#create data vault directory
dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())
dv.cd(['','Experiments', experimentName, dirappend], True )

globalDict = {
              'iterationsPerFreq':iterationsPerFreq,
              'experimentName':experimentName,  
              'comment':comment          
              }
pboxDict = {
            'sequence':pboxSequence,
            'number_of_pulses':number_of_pulses,
            'shutter_delay_time':shutter_delay_time,
            'heat_cool_delay':heat_cool_delay,
            'radial_heating_time':radial_heating_time,
            'cooling_ax_time':cooling_ax_time,
            }

parameters = Parameters(globalDict)
parameters.addDict(pboxDict)
parameters.printDict()

def extractHeatCoolCounts(timetags):
    #uses knowledge of the pulse sequence timing to extract the total counts for heating and cooling cycles
    cyclesStart = (shutter_delay_time + heat_cool_delay) * 10.0**-6 #in seconds
    binEdges = [cyclesStart]
    curStart = cyclesStart
    for i in range(int(number_of_pulses)):
        binEdges.append(curStart + (radial_heating_time) * 10.0**-6)
        binEdges.append(curStart + (radial_heating_time + heat_cool_delay) * 10.0**-6 )
        binEdges.append(curStart + (radial_heating_time + heat_cool_delay + cooling_ax_time) * 10.0**-6  )
        binEdges.append(curStart + (radial_heating_time + heat_cool_delay + cooling_ax_time + heat_cool_delay) * 10.0**-6 )
        curStart = curStart + (radial_heating_time + heat_cool_delay + cooling_ax_time + heat_cool_delay) * 10.0**-6 
    binnedCounts = numpy.histogram(timetags, binEdges)[0]
    binnedCounts = binnedCounts.reshape((number_of_pulses,4))
    summed = binnedCounts.sum(axis = 0)
    heatCounts = summed[0]
    coolCounts = summed[2]
    return [heatCounts,coolCounts]
    
def initialize():
    trfpga.set_time_length(recordTime)
    paulsbox.program(pbox, pboxDict)
    #make sure r&s synthesizers are on and go into auto mode
    for name in ['axial','radial']:
        dpass.select(name)
        dpass.output(True)
    for name in ['axial','radial','global']:
        trigger.switch_auto(name,False)
    #set up dataprocessing inputs
    resolution = trfpga.get_resolution()
    dp.set_inputs('timeResolvedBinning',[('timelength',recordTime),('resolution',resolution),('bintime',binTime)])
    
def sequence():
    binnedFlour = numpy.zeros(binNumber)
    dpass.select('radial')
    initfreq = dpass.frequency()
    for freqIteration,freq in enumerate(scanList):
        print 'frequency now {}'.format(freq)
        dpass.frequency(freq)
        for iteration in range(iterationsPerFreq):
            print 'recording trace {0} out of {1}'.format(iteration, iterationsPerFreq)
            trfpga.perform_time_resolved_measurement()
            trigger.trigger('PaulBox')
            timetags = trfpga.get_result_of_measurement().asarray
            #saving timetags
            dv.cd(['','Experiments', experimentName, dirappend, 'timetags'],True )
            dv.new('timetags {0} {1}'.format(freq,iteration),[('Time', 'sec')],[('PMT counts','Arb','Arb')] )
            dv.add_parameter('frequency', freq)
            dv.add_parameter('iteration',iteration)
            ones = numpy.ones_like(timetags)
            dv.add(numpy.vstack((timetags,ones)).transpose())
            #add to binning of the entire sequence
            newbinned = numpy.histogram(timetags, binArray )[0]
            binnedFlour = binnedFlour + newbinned
            newHeatCounts,newCoolCounts = extractHeatCoolCounts(timetags)
            heatCountsArray[freqIteration] += newHeatCounts
            coolCountsArray[freqIteration] += newCoolCounts
            trigger.wait_for_pbox_completion()
            trigger.wait_for_pbox_completion() #have to call twice until bug is fixed
        print 'getting result and adding to data vault'
        dv.cd(['','Experiments', experimentName, dirappend] )
        dv.new('binnedFlourescence {}'.format(freq),[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
        data = numpy.vstack((binArray[0:-1], binnedFlour)).transpose()
        dv.add(data)
    print 'adding line scan to data vault'
    data = numpy.vstack((scanList, heatCountsArray, coolCountsArray)).transpose()
    dv.cd(['','Experiments', experimentName, dirappend] )
    dv.new('lineScan',[('Freq', 'sec')], [('PMT counts','Heating','Counts'),('PMT counts','Cooling','Counts')] )
    dv.add(data)
    dv.add_parameter('plotLive',True)
    measureList = ['trapdrive','endcaps','compensation','dcoffsetonrf','cavity397','cavity866','multiplexer397','multiplexer866','axialDP','radialDP']
    measuredDict = dvParameters.measureParameters(cxn, measureList)
    dvParameters.saveParameters(dv, measuredDict)
    dvParameters.saveParameters(dv, globalDict)
    dvParameters.saveParameters(dv, pboxDict)
    print 'switching beams back into manual mode'
    for name in ['axial','radial','global']:
        trigger.switch_manual(name)
    dpass.frequency(initfreq)
    
print 'initializing measurement'
initialize()
print 'performing sequence'
sequence()
print 'DONE'