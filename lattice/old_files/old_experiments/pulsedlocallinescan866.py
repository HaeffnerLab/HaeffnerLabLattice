import sys; sys.path.append('C:\\Users\\lattice\\Desktop\\LabRAD\\lattice\\scripts')
import labrad
import numpy
import time
from scriptLibrary.parameter import Parameters
from scriptLibrary import paulsbox 
from scriptLibrary import dvParameters 

"""performing line scan with repeated pulses of the 866 DP"""

experimentName = 'PulsedLocalLineScan866'
comment = 'no comment'
iterations = 10
pboxSequence = 'PulsedLocalLineScan866.py' 
number_of_pulses = 41.0 #matches the number of steps in the RS LIST
pulse_length = 10.0*10**3#micrseconds
off_time = 2.0*10**3 #microseconds
recordTime =  number_of_pulses * (pulse_length + off_time)  / (1.0*10**6) #in seconds
#data processing on the fly
binTime =50.0*10**-6
binNumber = int(recordTime / binTime)
binArray = binTime * numpy.arange(binNumber + 1)

#connect connect and define servers we'll be using
cxn = labrad.connect()
dv = cxn.data_vault
dpass = cxn.double_pass
trigger = cxn.trigger
pbox = cxn.paul_box
trfpga = cxn.timeresolvedfpga
reg = cxn.registry
dp866 = cxn.rohdeschwarz_server
dp866.select_device('lattice-pc GPIB Bus - USB0::0x0AAD::0x0054::102549') #selecting 866DP R&S

#create data vault directory
dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())
dv.cd(['','Experiments', experimentName, dirappend], True )

globalDict = {
              'iterations':iterations,
              'experimentName':experimentName,  
              'comment':comment          
              }

pboxDict = {
            'sequence':pboxSequence,
            'number_of_pulses':number_of_pulses,
            'off_time':off_time,
            'pulse_length':pulse_length
            }

parameters = Parameters(globalDict)
parameters.addDict(pboxDict)
parameters.printDict()

#def extractHeatCoolCounts(timetags):
#    #uses knowledge of the pulse sequence timing to extract the total counts for heating and cooling cycles
#    cyclesStart = (shutter_delay_time + heat_cool_delay) * 10.0**-6 #in seconds
#    binEdges = [cyclesStart]
#    curStart = cyclesStart
#    for i in range(int(number_of_pulses)):
#        binEdges.append(curStart + (radial_heating_time) * 10.0**-6)
#        binEdges.append(curStart + (radial_heating_time + heat_cool_delay) * 10.0**-6 )
#        binEdges.append(curStart + (radial_heating_time + heat_cool_delay + cooling_ax_time) * 10.0**-6  )
#        binEdges.append(curStart + (radial_heating_time + heat_cool_delay + cooling_ax_time + heat_cool_delay) * 10.0**-6 )
#        curStart = curStart + (radial_heating_time + heat_cool_delay + cooling_ax_time + heat_cool_delay) * 10.0**-6 
#    binnedCounts = numpy.histogram(timetags, binEdges)[0]
#    binnedCounts = binnedCounts.reshape((number_of_pulses,4))
#    summed = binnedCounts.sum(axis = 0)
#    heatCounts = summed[0]
#    coolCounts = summed[2]
#    return [heatCounts,coolCounts]

def initialize():
    trfpga.set_time_length(recordTime)
    paulsbox.program(pbox, pboxDict)
    #make sure r&s synthesizers are on and go into auto mode
    for name in ['repump']:
        dpass.select(name)
        dpass.output(True)
    for name in ['866DP']:
        trigger.switch_auto(name)
    dp866.activate_list_mode(True)
    #set up dataprocessing inputs
    resolution = trfpga.get_resolution()
    
def sequence():
    binnedFlour = numpy.zeros(binNumber)
    for iteration in range(iterations):
        print 'iteration {}'.format(iteration)
        trfpga.perform_time_resolved_measurement()
        dp866.reset_list() #should reset here 
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
        trigger.wait_for_pbox_completion()
        trigger.wait_for_pbox_completion() #have to call twice until bug is fixed
    print 'getting result and adding to data vault'
    dv.cd(['','Experiments', experimentName, dirappend] )
    dv.new('binnedFlourescence'.format(),[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
    data = numpy.vstack((binArray[0:-1], binnedFlour)).transpose()
    dv.add(data)
    dv.add_parameter('plotLive',True)
    #finalizing
    measureList = ['trapdrive','endcaps','compensation','dcoffsetonrf','cavity397','cavity866','multiplexer397','multiplexer866','axialDP','radialDP']
    #measuredDict = dvParameters.measureParameters(cxn, measureList)
    #dvParameters.saveParameters(dv, measuredDict)
    dvParameters.saveParameters(dv, globalDict)
    dvParameters.saveParameters(dv, pboxDict)
    print 'switching beams back into manual mode'
    for name in ['axial','radial']:
        trigger.switch_manual(name)
    dp866.activate_list_mode(False)

print 'initializing measurement'
initialize()
print 'performing sequence'
sequence()
print 'DONE'