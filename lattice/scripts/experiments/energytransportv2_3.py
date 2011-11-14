import sys; sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
import labrad
import numpy
import time
import os
from scriptLibrary import registry
from scriptLibrary.parameter import Parameters
from scriptLibrary import paulsbox 
from scriptLibrary import dvParameters 

''' Ability to perform a scan of double pass'''

#Global parameters
comment = '5 ions'
iterations = 200
experimentName = 'EnergyTransportv2'
rawSaveDir = 'rawdata'
#radial double pass scan
freqmin = 250.0 #MHz
freqmax = 210.0 #MHz
freq_points = 5
radOffset = 0.0 #how much to offset calibrated radial power
freqList =  numpy.r_[freqmin:freqmax:complex(0,freq_points)]
#Paul's Box Parameters
pboxsequence = 'EnergyTransportv5.py'
equilibration_time = 10.*10**3
radial_heating_time = 100.0*10**3
record_866off_time = 10.*10**3
record_866on_time = 10.*10**3
shutter_delay_time = 20.*10**3
axial_on_time = 100.*10**3
diffax = 10.*10**3
global_off_time = equilibration_time + radial_heating_time  + 50.*10**3
#Time Resolved Recording
record_after_heating = 100.*10**3
recordTime = (record_866off_time + record_866on_time + 2 * shutter_delay_time + equilibration_time + radial_heating_time + record_after_heating)/10**6 #seconds
#data processing on the fly
binTime =250*10**-6 #seconds

globalDict = {
              'iterations':iterations,
              'experimentName':experimentName,
              'rawSaveDir':rawSaveDir,
              'scanRadfreqmin':freqmin,
              'scanRadfreqmax':freqmax,
              'scamRadfreqpts':freq_points,
              'radialOffset':radOffset,  
              'comment':comment          
              }
pboxDict = {
            'sequence':pboxsequence,
            'global_off_time':global_off_time,
            'equilibration_time':equilibration_time,
            'radial_heating_time':radial_heating_time,
            'shutter_delay_time':shutter_delay_time,
            'axial_on_time':axial_on_time,
            'diffax':diffax
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
    #make sure r&s synthesizers are on, and 
    for name in ['radial']:
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
    #where to save into datavault
    dv.cd(['','Experiments', experimentName, dirappend], True )
    #make sure we are running in the calibrated mode
#    dpass.select('radial')
#    dpass.amplitude_offset(radOffset)

def sequence():
    for radfreq in freqList:
        #start new dataprocessing process
        dp.new_process('timeResolvedBinning')
        dpass.frequency(radfreq)
        for iteration in range(iterations):
            print 'recording trace {0} out of {1} with frequency {2}'.format(iteration, iterations, radfreq)
            print 'now perform measurement'
            trfpga.perform_time_resolved_measurement()
            print 'now trigger'
            trigger.trigger('PaulBox')
            print 'now get result'
            (arrayLength, timeLength, timeResolution), measuredData = trfpga.get_result_of_measurement()
            measuredData = measuredData.asarray
            infoarray = numpy.array([arrayLength,timeLength,timeResolution])
            saveName = 'trace{}'.format(iteration)
            print 'now saving {}'.format(saveName)
            numpy.savez(saveName,measuredData, infoarray)
            print 'now adding to dataprocessing server'
            dp.process_new_data('timeResolvedBinning',measuredData)
            print 'now waiting to complete recooling'
            trigger.wait_for_pbox_completion()
            trigger.wait_for_pbox_completion() #have to call twice until bug is fixed
        print 'getting result and adding to data vault'
        binned = dp.get_result('timeResolvedBinning').asarray
        dv.new('binnedFlourescence freq {}'.format(radfreq),[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
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
print 'DONE'
