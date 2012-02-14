import sys; sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
import labrad
import numpy
import time
import os
from scriptLibrary.parameter import Parameters
from scriptLibrary import paulsbox 
from scriptLibrary import dvParameters 

'''Rf Heating'''
#Global parameters
comment = 'using radial channel for rf heating'
iterations = 1000
experimentName = 'RFheat'
#Paul's Box Parameters
pboxsequence = 'RFheat.py'
start_rf = 0.0
rf_duration = 60.*10**3
record_866off_time = 5*10**3
recordTime = (start_rf + 40.*10**3 + rf_duration + 2 * record_866off_time) / 10**6
#recordTime = (1 * record_866off_time) / 10**6
#data processing on the fly
binTime =200.0*10**-6
binNumber = int(recordTime / binTime)
binArray = binTime * numpy.arange(binNumber + 1)

#connect and define servers we'll be using
cxn = labrad.connect()
dv = cxn.data_vault
dpass = cxn.double_pass
trigger = cxn.trigger
pbox = cxn.paul_box
trfpga = cxn.timeresolvedfpga
#create directory for file saving
dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())

globalDict = {
              'iterations':iterations,
              'experimentName':experimentName,    
              'comment':comment          
              }
pboxDict = {
            'sequence':pboxsequence,
            'start_rf':start_rf,
            'rf_duration':rf_duration,
            'record_866off_time':record_866off_time
            }

parameters = Parameters(globalDict)
parameters.addDict(pboxDict)

def initialize():
    trfpga.set_time_length(recordTime)
    paulsbox.program(pbox, pboxDict)
    #make sure manual overrides are off
    trigger.switch_auto('radial',  False)
    trigger.switch_auto('866DP',  True)
    #make sure r&s synthesizers are on
    #for name in ['axial','radial']:
     #   dpass.select(name)
     #   dpass.output(True)
    #globalDict['resolution']=trfpga.get_resolution()

def sequence():
    binnedFlour = numpy.zeros(binNumber)
    for iteration in range(iterations):
        print 'recording trace {0} out of {1}'.format(iteration, iterations-1)
        print 'perform'
        trfpga.perform_time_resolved_measurement()
        print 'trigger now'
        trigger.trigger('PaulBox')
        print 'get result'
        timetags = trfpga.get_result_of_measurement().asarray
        print 'got timetags now saving'
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
        print 'now sleeping'
        time.sleep(.2)
    print 'getting result and adding to data vault'
    dv.cd(['','Experiments', experimentName, dirappend] )
    dv.new('binnedFlourescence',[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
    data = numpy.vstack((binArray[0:-1], binnedFlour)).transpose()
    dv.add(data)
    dv.add_parameter('plotLive',True)

def finalize():
    measureList = ['trapdrive','endcaps','compensation','dcoffsetonrf','cavity397','cavity866','multiplexer397','multiplexer866','radialDP']
    measuredDict = dvParameters.measureParameters(cxn, measureList)
    dvParameters.saveParameters(dv, measuredDict)
    dvParameters.saveParameters(dv, globalDict)
    dvParameters.saveParameters(dv, pboxDict)
    for name in ['radial']:
        trigger.switch_manual(name)
        
print 'initializing measurement'
initialize()
print 'performing sequence'
sequence()
print 'finalizing measurement'
finalize()                                                                                                                                                                                                                     
print 'DONE'