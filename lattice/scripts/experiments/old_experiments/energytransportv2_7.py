import sys; sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
import labrad
import numpy
import time
import os
from scriptLibrary.parameter import Parameters
from scriptLibrary import paulsbox 
from scriptLibrary import dvParameters 

''' Ability to change heating detunings with the doulbe pass'''

#Global parameters
comment = '4 ions: axial calibrate'
iterations = 100
experimentName = 'EnergyTransportv2'
#radial double pass scan
freqmin = 250.0 #MHz
freqmax = 250.0 #MHz
freq_points = 1
radOffset = 0.0 #how much to offset calibrated radial power
freqList =  numpy.r_[freqmin:freqmax:complex(0,freq_points)]
#Paul's Box Parameters
pboxsequence = 'EnergyTransportv5.py'
equilibration_time = 10.*10**3
radial_heating_time =100.0*10**3
record_866off_time = 10.*10**3
record_866on_time = 10.*10**3
shutter_delay_time = 20.*10**3
axial_on_time = 10.*10**3
diffax = 10.*10**3
global_off_time = equilibration_time + radial_heating_time  + 50.*10**3
#Time Resolved Recording
record_after_heating = 100.*10**3
recordTime = (record_866off_time + record_866on_time + 2 * shutter_delay_time + equilibration_time + radial_heating_time + record_after_heating)/10**6 #seconds
#data processing on the fly
binTime =250.0*10**-6
binNumber = int(recordTime / binTime)
binArray = binTime * numpy.arange(binNumber + 1)

globalDict = {
              'iterations':iterations,
              'experimentName':experimentName,
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

dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())

def initialize():
    trfpga.set_time_length(recordTime)
    paulsbox.program(pbox, pboxDict)
    #make sure manual override for the 397 local heating beam is off
    for name in ['global','radial','866DP']:
        trigger.switch_auto(name,  False)
    trigger.switch_auto('axial',  True)
    #make sure r&s synthesizers are on, and 
    for name in ['radial']:
        dpass.select(name)
        dpass.output(True)
    globalDict['resolution']=trfpga.get_resolution()
    
def sequence():
    binnedFlour = numpy.zeros(binNumber)
    for radfreq in freqList:
        #start new dataprocessing process
        dpass.frequency(radfreq)
        for iteration in range(iterations):
            print 'recording trace {0} out of {1} with frequency {2}'.format(iteration, iterations, radfreq)
            print 'now perform measurement'
            trfpga.perform_time_resolved_measurement()
            print 'now trigger'
            trigger.trigger('PaulBox')
            print 'now get result'
            timetags = trfpga.get_result_of_measurement().asarray
            #saving timetags
            dv.cd(['','Experiments', experimentName, dirappend, 'timetags'],True )
            dv.new('timetags {0} {1}'.format(radfreq,iteration),[('Time', 'sec')],[('PMT counts','Arb','Arb')] )
            dv.add_parameter('frequency', radfreq)
            dv.add_parameter('iteration',iteration)
            ones = numpy.ones_like(timetags)
            dv.add(numpy.vstack((timetags,ones)).transpose())
            #add to binning of the entire sequence
            newbinned = numpy.histogram(timetags, binArray )[0]
            binnedFlour = binnedFlour + newbinned
            print 'now waiting to complete recooling'
            trigger.wait_for_pbox_completion()
            trigger.wait_for_pbox_completion() #have to call twice until bug is fixed
        print 'getting result and adding to data vault'
        dv.cd(['','Experiments', experimentName, dirappend] )
        dv.new('binnedFlourescence'.format(radfreq),[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
        data = numpy.vstack((binArray[0:-1], binnedFlour)).transpose()
        dv.add(data)
        print 'gathering parameters and adding them to data vault'
        measureList = ['trapdrive','endcaps','compensation','dcoffsetonrf','cavity397','cavity866','multiplexer397','multiplexer866','axialDP','radialDP']
        measuredDict = dvParameters.measureParameters(cxn, measureList)
        dvParameters.saveParameters(dv, measuredDict)
        dvParameters.saveParameters(dv, globalDict)
        dvParameters.saveParameters(dv, pboxDict)

def finalize():
    for name in ['axial','radial','global']:
        trigger.switch_manual(name)
        
print 'initializing measurement'
initialize()
print 'performing sequence'
sequence()
print 'finalizing'
finalize()
print 'DONE'
