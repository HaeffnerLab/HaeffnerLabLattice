import labrad
import numpy
import time
import os
#global parameters
##Timing for Paul's Box Sequence, all in microseconds
pboxSequence = 'AxialHeatingRatev2.py' 
backgroundMeasureTime = 10.*10**3 #microseconds
axialOffTime = 500.*10**3#microseconds
recoolingTime = 10.*10**3 #microseconds
iterations = 200# #how many traces to take
radialOnTime = 1.*10**3 #microseconds
radialOffTime = 150.*10**3 #microseconds
recordTime = (backgroundMeasureTime + axialOffTime + recoolingTime + 10000)/10**6 #in seconds
#data processing on the fly
binTime =250*10**-6 #seconds
#connect
cxn = labrad.connect()
#define servers we'll be using
dv = cxn.data_vault
dpass = cxn.double_pass
trigger = cxn.trigger
pbox = cxn.paul_box
trfpga = cxn.timeresolvedfpga
dp = cxn.dataprocessor

print '############################################'
print 'STARTING EXPERIMENT Axial Heating'
print 'Executing Paul Box Sequence {}'.format(pboxSequence)
print 'Background measurement time {} microseconds'.format(backgroundMeasureTime)
print 'Axial Time Off {} microseconds'.format(axialOffTime)
print 'Recooling Time {} microseconds'.format(recoolingTime)
print 'Radial On Time {} microseconds'.format(radialOnTime)
print "Radial Off Time {} microseconds".format(radialOffTime)
print 'Recording Time Resolved Flourescence for {} seconds'.format(recordTime)
print 'Recording {} traces '.format(iterations)
print '############################################'

def initialize():
    #set recording time length for time resolved counts
    trfpga.set_time_length(recordTime)
    #program paul box script
    progArray = [
                 ['FLOAT','background_meas_time',str(backgroundMeasureTime)],
                 ['FLOAT','axial_off_time',str(axialOffTime)],
                 ['FLOAT','recooling_time',str(recoolingTime)],
                 ['FLOAT','radial_on_time',str(radialOnTime)],
                 ['FLOAT','radial_off_time',str(radialOffTime)]
                 ]
    pbox.send_command(pboxSequence,progArray)
    #make sure manual override for the 397 local heating beam is off
    trigger.switch('axial',False)
    #make sure r&s synthesizers are on
    for name in ['axial','radial']:
        dpass.select(name)
        dpass.output(True)
    #create directory for file saving
    dirappend = time.asctime().replace(' ','').replace(':','')
    directory = os.getcwd() + '\\' + dirappend
    os.mkdir(directory)
    os.chdir(directory)
    #set dataprocessing inputs
    resolution = trfpga.get_resolution()
    dp.set_inputs('timeResolvedBinning',[('timelength',recordTime),('resolution',resolution),('bintime',binTime)])
    dp.new_process('timeResolvedBinning')
    #where to save into datavault
    dv.cd(['','Experiments', 'axialheatingv2',dirappend], True )
    
def sequence():
    for iteration in range(iterations):
        print 'recording trace {0} out of {1}'.format(iteration, iterations)
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
        #time.sleep(0.1)
        print 'getting result and adding to data vault'
    binned = dp.get_result('timeResolvedBinning').asarray
    dv.new('binnedFlourescence',[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
    dv.add(binned)
        
print 'initializing parameters'
initialize()
print 'performing sequence'
sequence()
print 'DONE'




