import sys; sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
import labrad
import numpy
import time
import os
from scriptLibrary import registry
from scriptLibrary.parameter import Parameters
from scriptLibrary import paulsbox 
from scriptLibrary import dvParameters 

'''Trying to measure speed of sound velocity'''
#Global parameters
comment = 'now testing together'
iterations = 10000
experimentName = 'EnergyTransportv3'
rawSaveDir = 'rawdata'
#Paul's Box Parameters
pboxsequence = 'EnergyTransportv3.py'
equilibration_time = 10.*10**3
radial_heating_time = 1.*10**3
shutter_delay_time = 20.*10**3
global_off_time = equilibration_time + radial_heating_time  + 50.*10**3
record_offset = 100.0
#Time Resolved Recording
recordAfterHeat = 500.0
recordTime = (record_offset + recordAfterHeat) / 10**6
#data processing on the fly
binTime = 1.0 * 10**-6 #seconds


globalDict = {
              'iterations':iterations,
              'experimentName':experimentName,
              'rawSaveDir':rawSaveDir,    
              'comment':comment          
              }
pboxDict = {
            'sequence':pboxsequence,
            'global_off_time':global_off_time,
            'equilibration_time':equilibration_time,
            'radial_heating_time':radial_heating_time,
            'record_offset':record_offset,
            'shutter_delay_time':shutter_delay_time
            }

parameters = Parameters(globalDict)
parameters.addDict(pboxDict)
parameters.printDict()
#connect and define servers we'll be using
cxn = labrad.connect()
dv = cxn.data_vault
dpass = cxn.double_pass
trigger = cxn.trigger
pbox = cxn.paul_box
trfpga = cxn.timeresolvedfpga
dp = cxn.dataprocessor
reg = cxn.registry
 
def initialize():
    trfpga.set_time_length(recordTime)
    paulsbox.program(pbox, pboxDict)
    #make sure manual override for the 397 local heating beam is off
    trigger.switch('axial',False)
    #make sure r&s synthesizers are on
    for name in ['axial','radial']:
        dpass.select(name)
        dpass.output(True)
    #create directory for file saving
    dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())
    basedir = registry.getDataDirectory(reg)
    directory = basedir + '\\' + rawSaveDir + '\\' + experimentName  + '\\' + dirappend
    os.mkdir(directory)
    os.chdir(directory)
    #set up dataprocessing inputs
    resolution = trfpga.get_resolution()
    dp.set_inputs('timeResolvedBinning',[('timelength',recordTime),('resolution',resolution),('bintime',binTime)])
    dp.new_process('timeResolvedBinning')
    #where to save into datavault
    dv.cd(['','Experiments', experimentName, dirappend], True )
    
def sequence():
    for iteration in range(iterations):
        print 'recording trace {0} out of {1}'.format(iteration, iterations)
#        print 'now perform measurement'
        trfpga.perform_time_resolved_measurement()
#        print 'now trigger'
        trigger.trigger('PaulBox')
#        print 'now get result'
        (arrayLength, timeLength, timeResolution), measuredData = trfpga.get_result_of_measurement()
        measuredData = measuredData.asarray
        infoarray = numpy.array([arrayLength,timeLength,timeResolution])
        saveName = 'trace{}'.format(iteration)
#        print 'now saving {}'.format(saveName)
        numpy.savez(saveName,measuredData, infoarray)
#        print 'now adding to dataprocessing server'
        dp.process_new_data('timeResolvedBinning',measuredData)
#        print 'now waiting to complete recooling'
        trigger.wait_for_pbox_completion()
        trigger.wait_for_pbox_completion() #have to call twice until bug is fixed

def finalize():
    print 'getting result and adding to data vault'
    binned = dp.get_result('timeResolvedBinning').asarray
    dv.new('binnedFlourescence',[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
    dv.add(binned)
    print 'gathering parameters and adding them to data vault'
    measureList = ['trapdrive','endcaps','compensation','dcoffsetonrf','cavity397','cavity866','multiplexer397','multiplexer866','axialDP','radialDP']
    measuredDict = dvParameters.measureParameters(cxn, measureList)
    dvParameters.saveParameters(dv, measuredDict)
    dvParameters.saveParameters(dv, globalDict)
    dvParameters.saveParameters(dv, pboxDict)
    
print 'initializing measurement'
initialize()
print 'performing sequence'
sequence()
print 'finalizing measurement'
finalize()
print 'DONE'