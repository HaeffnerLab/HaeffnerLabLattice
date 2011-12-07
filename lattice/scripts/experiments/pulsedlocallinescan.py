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
rawSaveDir = 'rawdata'
NUM_STEP_FREQ = 2
MIN_FREQ = 220.0 #MHZ
MAX_FREQ = 250.0 #MHZ
scanList = numpy.r_[MIN_FREQ:MAX_FREQ:complex(0,NUM_STEP_FREQ)]
##Timing for Paul's Box Sequence, all in microseconds
pboxSequence = 'PulsedLocalLineScan.py' 
number_of_pulses = 200.0
shutter_delay_time = 20.*10**3 #microseconds
heat_cool_delay = 100.0#microseconds
radial_heating_time = 1.*10**3 #microseconds
cooling_ax_time = 1.*10**3 #microseconds
iterationsPerFreq = 1#how many traces to take at each frequency
##timing for time resolved recording
recordTime =  (shutter_delay_time + number_of_pulses * (2 * heat_cool_delay + radial_heating_time + cooling_ax_time)) / 10**6 #in seconds
#data processing on the fly
binTime =50*10**-6
#connect connect and define servers we'll be using
cxn = labrad.connect()
dv = cxn.data_vault
dpass = cxn.double_pass
trigger = cxn.trigger
pbox = cxn.paul_box
trfpga = cxn.timeresolvedfpga
dp = cxn.dataprocessor
reg = cxn.registry

globalDict = {
              'iterationsPerFreq':iterationsPerFreq,
              'experimentName':experimentName,
              'rawSaveDir':rawSaveDir,    
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
    #create data vault directory
    dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())
    dv.cd(['','Experiments', experimentName, dirappend], True )
    
def sequence():
    dpass.select('radial')
    initfreq = dpass.frequency()
    for freq in scanList:
        print 'frequency now {}'.format(freq)
        dpass.frequency(freq)
        dp.new_process('timeResolvedBinning')
        for iteration in range(iterationsPerFreq):
            print 'recording trace {0} out of {1}'.format(iteration, iterationsPerFreq)
            trfpga.perform_time_resolved_measurement()
            trigger.trigger('PaulBox')
            timetags = trfpga.get_result_of_measurement().asarray
            binned = numpy.histogram(timetags, bins, range, normed, weights, density)
            



            trigger.wait_for_pbox_completion()
            trigger.wait_for_pbox_completion() #have to call twice until bug is fixed
        print 'getting result and adding to data vault'
        binned = dp.get_result('timeResolvedBinning').asarray
        dv.new('binnedFlourescence {}'.format(freq),[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
        dv.add(binned)
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