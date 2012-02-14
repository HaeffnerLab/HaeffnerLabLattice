import sys; sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
import labrad
import numpy
import time
import os
from scriptLibrary.parameter import Parameters
from scriptLibrary import paulsbox 
from scriptLibrary import dvParameters 

'''Trying to measure speed of sound'''
#Global parameters
comment = ''
iterations = 300
experimentName = 'SoundVelocity'
#Paul's Box Parameters
pboxsequence = 'SoundVelocity.py'
shutter_delay_time = 20.*10**3
start_radial = 0.0
start_axial = 0.0
radial_duration = 10.*10**3
axial_duration = 10.*10**3
off866time = 5*10**3
#Time Resolved Recording
recordTime = (shutter_delay_time + 2 * off866time + max(start_radial + radial_duration, start_axial + axial_duration) + 10.*10**3) / 10**6
#data processing on the fly
binTime =5.0*10**-6
binNumber = int(recordTime / binTime)
binArray = binTime * numpy.arange(binNumber + 1)
#create directory for file saving
dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())

globalDict = {
              'iterations':iterations,
              'experimentName':experimentName,    
              'comment':comment          
              }
pboxDict = {
            'sequence':pboxsequence,
            'shutter_delay_time':shutter_delay_time,
            'start_radial':start_radial,
            'start_axial':start_axial,
            'radial_duration':radial_duration,
            'axial_duration':axial_duration,
            'off866time':off866time
            }

parameters = Parameters(globalDict)
parameters.addDict(pboxDict)
#connect and define servers we'll be using
cxn = labrad.connect()
dv = cxn.data_vault
dpass = cxn.double_pass
trigger = cxn.trigger
pbox = cxn.paul_box
trfpga = cxn.timeresolvedfpga
 
def initialize():
    trfpga.set_time_length(recordTime)
    paulsbox.program(pbox, pboxDict)
    #make sure manual override for the 397 local heating beam is off
    for name in ['global','radial','axial','866DP']:
        trigger.switch_auto(name,  False)
    #make sure r&s synthesizers are on
    for name in ['axial','radial']:
        dpass.select(name)
        dpass.output(True)
    globalDict['resolution']=trfpga.get_resolution()
    
def sequence():
    binnedFlour = numpy.zeros(binNumber)
    for iteration in range(iterations):
        print 'recording trace {0} out of {1}'.format(iteration, iterations-1)
        trfpga.perform_time_resolved_measurement()
        trigger.trigger('PaulBox')
        timetags = trfpga.get_result_of_measurement().asarray
        #saving timetags
        dv.cd(['','Experiments', experimentName, dirappend, 'timetags'],True )
        dv.new('timetags {0}'.format(iteration),[('Time', 'sec')],[('PMT counts','Arb','Arb')] )
        dv.add_parameter('iteration',iteration)
        ones = numpy.ones_like(timetags)
        dv.add(numpy.vstack((timetags,ones)).transpose())
        #add to binning of the entire sequence
        newbinned = numpy.histogram(timetags, binArray )[0]
        binnedFlour = binnedFlour + newbinned
        print 'now waiting to complete the sequence'
        trigger.wait_for_pbox_completion()
        trigger.wait_for_pbox_completion() #have to call twice until bug is fixed
    print 'getting result and adding to data vault'
    dv.cd(['','Experiments', experimentName, dirappend] )
    dv.new('binnedFlourescence',[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
    data = numpy.vstack((binArray[0:-1], binnedFlour)).transpose()
    dv.add(data)
    dv.add_parameter('plotLive',True)

def finalize():
    measureList = ['trapdrive','endcaps','compensation','dcoffsetonrf','cavity397','cavity866','multiplexer397','multiplexer866','axialDP','radialDP']
    measuredDict = dvParameters.measureParameters(cxn, measureList)
    dvParameters.saveParameters(dv, measuredDict)
    dvParameters.saveParameters(dv, globalDict)
    dvParameters.saveParameters(dv, pboxDict)
    for name in ['axial','radial','global']:
        trigger.switch_manual(name)
    
print 'initializing measurement'
initialize()
print 'performing sequence'
sequence()
print 'finalizing measurement'
finalize()
print 'DONE'