import sys; sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
import labrad
import numpy
import time
import os
from scriptLibrary.parameter import Parameters
from scriptLibrary import paulsbox 
from scriptLibrary import dvParameters 

''' Ability to scan the detunings of both double passes and run two different pulse sequences:
RadialHeating.py for heating with radial beam (axial beam needed before and after for cooling)
or SoundVelocity.py where we specify start and stop time for each beam.'''

#Global parameters
comment = 'no comment'
iterations = 100
experimentName = 'Heating'
#radial double pass scan
radfreqmin = 220.0 #MHz
radfreqmax = 220.0 #MHz
radfreq_points = 1
radFreqList =  numpy.r_[radfreqmin:radfreqmax:complex(0,radfreq_points)]
#axial double pass scan
axfreqmin = 220.0 #MHz
axfreqmax = 220.0 #MHz
axfreq_points = 1
axFreqList =  numpy.r_[axfreqmin:axfreqmax:complex(0,axfreq_points)]
heatWithRadial = True
heatArbitrary =  not heatWithRadial
heatArbitraryRadOn = True


globalDict = {
              'iterations':iterations,
              'experimentName':experimentName,
              'radfreqmin':radfreqmin,
              'radfreqmax':radfreqmax,
              'radfreqpts':radfreq_points,
              'axfreqmin':axfreqmin,
              'axfreqmax':axfreqmax,
              'axfreqpts':axfreq_points,
              'comment':comment          
              }

if heatWithRadial:
    #heating with the radial beam    
    #Paul's Box Parameters
    pboxsequence = 'RadialHeating.py'
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

    pboxDict = {
                'sequence':pboxsequence,
                'global_off_time':global_off_time,
                'equilibration_time':equilibration_time,
                'radial_heating_time':radial_heating_time,
                'shutter_delay_time':shutter_delay_time,
                'axial_on_time':axial_on_time,
                'diffax':diffax
                }
    globalDict['recordTime'] = recordTime
    
if heatArbitrary:
    pboxsequence = 'SoundVelocity.py'
    shutter_delay_time = 20.*10**3
    start_radial = 0.0
    start_axial = 0.0
    radial_duration = 10.*10**3
    axial_duration = 10.*10**3
    off866time = 5*10**3
    #Time Resolved Recording
    recordTime = (shutter_delay_time + 2 * off866time + max(start_radial + radial_duration, start_axial + axial_duration) + 10.*10**3) / 10**6   
    pboxDict = {
            'sequence':pboxsequence,
            'shutter_delay_time':shutter_delay_time,
            'start_radial':start_radial,
            'start_axial':start_axial,
            'radial_duration':radial_duration,
            'axial_duration':axial_duration,
            'off866time':off866time
            }
    globalDict['recordTime'] = recordTime


#data processing on the fly
binTime =250.0*10**-6
binNumber = int(recordTime / binTime)
binArray = binTime * numpy.arange(binNumber + 1)

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
    if heatWithRadial:
    #make sure all beams are auto controlled. axial needs to be inverted to provide cooling in between sequences
        for name in ['global','radial','866DP']:
            trigger.switch_auto(name,  False)
        trigger.switch_auto('axial',  True)
    elif heatArbitrary:
        for name in ['global','radial','axial','866DP']:
            trigger.switch_auto(name,  False)
        if not heatArbitraryRadOn:
            trigger.switch_manual('radial', False)
    #make sure r&s synthesizers are on, and 
    for name in ['axial','radial']:
        dpass.select(name)
        dpass.output(True)
    globalDict['resolution']=trfpga.get_resolution()
    
def sequence():
    binnedFlour = numpy.zeros(binNumber)
    for radfreq in radFreqList:
        #start new dataprocessing process
        dpass.select('radial')
        dpass.frequency(radfreq)
        for axfreq in axFreqList:
            for iteration in range(iterations):
                print 'recording trace {0} out of {1} with rad frequency {2}, ax freq {3}'.format(iteration, iterations -1, radfreq, axfreq)
                trfpga.perform_time_resolved_measurement()
                trigger.trigger('PaulBox')
                timetags = trfpga.get_result_of_measurement().asarray
                #saving timetags
                dv.cd(['','Experiments', experimentName, dirappend, 'timetags'],True )
                dv.new('timetags rad{0} ax{1} iter{2}'.format(radfreq,axfreq, iteration),[('Time', 'sec')],[('PMT counts','Arb','Arb')] )
                dv.add_parameter('radfrequency', radfreq)
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
            print 'getting result and adding to data vault'
            dv.cd(['','Experiments', experimentName, dirappend] )
            dv.new('binnedFlourescence rad{0} ax{1}'.format(radfreq, axfreq),[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
            data = numpy.vstack((binArray[0:-1], binnedFlour)).transpose()
            dv.add(data)
            dv.add_parameter('plotLive',True)
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
