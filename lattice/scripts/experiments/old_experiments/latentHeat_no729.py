import sys; sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
import labrad
import numpy
import time
import os
from scriptLibrary.parameter import Parameters
from scriptLibrary import paulsbox 
from scriptLibrary import dvParameters 

''''
This experiment involves studying the sharpness of crystal to cloud phase transition. After all cooling lights are switched off,
the crystal is heated with far blue light for a variable time. Readout is meant to be done with a near resonant red light,
and we need a far red global beam to be able to crystallize the chain again.
'''

#Global parameters
comment = 'no comment'
iterations = 10
experimentName = 'LatentHeat_no729'
#axial double pass scan
axfreqmin = 250.0 #MHz
axfreqmax = 250.0 #MHz
axfreq_points = 1
axFreqList =  numpy.r_[axfreqmin:axfreqmax:complex(0,axfreq_points)]

pboxsequence = 'LatentHeat_no729.py'
global_off_start = 50.*10**3
crystallize_delay = 25.*10**3
how_many_exposures = 1
shutter_delay = 20.*10**3
camera_exposure =  50.*10**3####
crystallize_time = 2000.*10**3
axial_heat = 60*10**3
heat_delay = 10.*10**3
readout_delay = 100.*10**3
#Time Resolved Recording
recordTime = min(.55, (heat_delay + readout_delay + axial_heat + shutter_delay + global_off_start + crystallize_delay + crystallize_time) / 10.0**6)   

globalDict = {
              'iterations':iterations,
              'experimentName':experimentName,
              'axfreqmin':axfreqmin,
              'axfreqmax':axfreqmax,
              'axfreqpts':axfreq_points,
              'recordTime':recordTime,
              'comment':comment   
              }

pboxDict = {
        'sequence':pboxsequence,
        'global_off_start':global_off_start,
        'crystallize_delay':crystallize_delay,
        'how_many_exposures':how_many_exposures,
        'shutter_delay':shutter_delay,
        'camera_exposure':camera_exposure,
        'crystallize_time':crystallize_time,
        'axial_heat':axial_heat,
        'heat_delay':heat_delay,
        'readout_delay':readout_delay
        }

#data processing on the fly
binTime =250.0*10**-6
binNumber = int(recordTime / binTime)
binArray = binTime * numpy.arange(binNumber + 1)
#
parameters = Parameters(globalDict)
parameters.addDict(pboxDict)
parameters.printDict()
#connect and define servers we'll be using
cxn = labrad.connect()
cxnlab = labrad.connect('192.168.169.49') #connection to labwide network
dv = cxn.data_vault
dpass = cxn.double_pass
trigger = cxn.trigger
pbox = cxn.paul_box
trfpga = cxn.timeresolvedfpga

dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())

def initialize():
    trfpga.set_time_length(recordTime)
    paulsbox.program(pbox, pboxDict)
    trigger.switch_auto('axial',  False) #axial needs to be inverted, so that high TTL corresponds to light on
    trigger.switch_auto('110DP',  True)
    trigger.switch_auto('crystallization',  True)
    #make sure r&s synthesizers are on, and 
    for name in ['110DP','axial']:
        dpass.select(name)
        dpass.output(True)
    globalDict['resolution']=trfpga.get_resolution()

def sequence():
    binnedFlour = numpy.zeros(binNumber)
    for axfreq in axFreqList:
        for iteration in range(iterations):
            print 'recording trace {0} out of {1} ax freq {2}'.format(iteration+1, iterations, axfreq)
            trfpga.perform_time_resolved_measurement()
            trigger.trigger('PaulBox')
            timetags = trfpga.get_result_of_measurement().asarray
            #saving timetags
            dv.cd(['','Experiments', experimentName, dirappend, 'timetags'],True )
            dv.new('timetags ax{0} iter{1}'.format(axfreq, iteration),[('Time', 'sec')],[('PMT counts','Arb','Arb')] )
            dv.add_parameter('axfrequency',axfreq)
            dv.add_parameter('iteration',iteration)
            ones = numpy.ones_like(timetags)
            dv.add(numpy.vstack((timetags,ones)).transpose())
            #add to binning of the entire sequence
            newbinned = numpy.histogram(timetags, binArray )[0]
            binnedFlour = binnedFlour + newbinned
            print 'now waiting to complete recooling'
            trigger.wait_for_pbox_completion()
            trigger.wait_for_pbox_completion() #have to call twice until bug is fixed
            #time.sleep(3.0)
        print 'getting result and adding to data vault'
        dv.cd(['','Experiments', experimentName, dirappend] )
        dv.new('binnedFlourescence ax{0}'.format(axfreq),[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
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
    for name in ['axial', '110DP','crystallization']:
        trigger.switch_manual(name)
            
print 'initializing measurement'
initialize()
print 'performing sequence'
sequence()
print 'finalizing'
finalize()
print 'DONE'
