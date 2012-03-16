import sys; sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
import labrad
import numpy
import time
import os
from scriptLibrary.parameter import Parameters
from scriptLibrary import paulsbox 
from scriptLibrary import dvParameters 

''''
The experiment involves first exposing the ions to 729 to mark a few dark. Then the global cooling is swtiched off and we heat
with far blue detuned axial beam. After that the global cooling is turned back on. Camera exposures are taken before and after
the heating so compare the positions of the dark ions.
'''

#Global parameters
comment = 'no comment'
iterations = 1
experimentName = 'LatentHeat'
#axial double pass scan
axfreqmin = 250.0 #MHz
axfreqmax = 250.0 #MHz
axfreq_points = 1
axFreqList =  numpy.r_[axfreqmin:axfreqmax:complex(0,axfreq_points)]

pboxsequence = 'LatentHeat.py'
shutter_delay_time = 20.*10**3
camera_exposure =  20.*10**3####
axial_heat = 50.*10**3
exposure_729 = 30.*10**3
global_off = 200.*10**3
#Time Resolved Recording
recordTime = (exposure_729 + 2 * shutter_delay_time + 2* camera_exposure + global_off) / 10.0**6   

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
        'shutter_delay_time':shutter_delay_time,
        'camera_exposure':camera_exposure,
        'axial_heat':axial_heat,
        'exposure_729':exposure_729,
        'global_off':global_off,
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
    trigger.switch_auto('global',  False)
    #make sure r&s synthesizers are on, and 
    for name in ['axial']:
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
    for name in ['axial', 'global']:
        trigger.switch_manual(name)
            
print 'initializing measurement'
initialize()
print 'performing sequence'
sequence()
print 'finalizing'
finalize()
print 'DONE'
