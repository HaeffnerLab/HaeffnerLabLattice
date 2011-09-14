import labrad
import numpy
import time
import os
#global parameters
##Frequency Scan of Local Heating Beam
MIN_FREQ = 190.0 #MHZ
MAX_FREQ = 250.0 #MHZ
STEP_FREQ = 10#MHZ
FreqScanList = numpy.arange(MIN_FREQ,MAX_FREQ + STEP_FREQ, STEP_FREQ)
##Timing for Paul's Box Sequence, all in microseconds
pboxSequence = 'LocalHeatingLineScan.py' 
backgroundMeasureTime = 25.*10**3
localHeatingTime = 50.*10**3
recoolingTime = 50.*10**3
iterationsPerFreq = 100 #how many traces to take at each frequency
recordTime =  (backgroundMeasureTime + localHeatingTime + recoolingTime) / 10**6 #in seconds
#connect
cxn = labrad.connect()
#define servers we'll be using
dv = cxn.data_vault
sigGen = cxn.rohdeschwarz_server
sigGen.select_device('lattice-pc GPIB Bus - USB0::0x0AAD::0x0054::104543')
trigger = cxn.trigger
pbox = cxn.paul_box
trfpga = cxn.timeresolvedfpga

print '############################################'
print 'STARTING EXPERIMENT Local Heating Line Scan'
print 'Scanning from {0} to {1} in steps of {2}'.format(MIN_FREQ, MAX_FREQ, STEP_FREQ)
print 'Executing Paul Box Sequence {}'.format(pboxSequence)
print 'Background measurement time {} microseconds'.format(backgroundMeasureTime)
print 'Heating Time using Local Beam {} microseconds'.format(localHeatingTime)
print 'Recooling Time {} microseconds'.format(recoolingTime)
print 'Recording Time Resolved Flourescence for {} seconds'.format(recordTime)
print 'Recording {} traces at each frequency'.format(iterationsPerFreq)
print '############################################'

def initialize():
    #set recording time length for time resolved counts
    trfpga.set_time_length(recordTime)
    #program paul box script
    progArray = [
                 ['FLOAT','background_meas_time',str(backgroundMeasureTime)],
                 ['FLOAT','local_heat_time',str(localHeatingTime)],
                 ['FLOAT','recooling_time',str(recoolingTime)],
                 ]
    pbox.send_command(pboxSequence,progArray)
    #make sure manual override for the 397 local heating beam is off
    trigger.switch('397LocalHeating',False)
    #create directory for file saving
    directory = os.getcwd() + '\\' + time.asctime().replace(' ','').replace(':','')
    os.mkdir(directory)
    os.chdir(directory)

def scan():
    for freq in FreqScanList:
        print 'setting frequency {}'.format(freq)
        sigGen.frequency(freq)
        for iteration in range(iterationsPerFreq):
            print 'recording trace {0} out of {1}'.format(iteration, iterationsPerFreq)
            print 'now perform measurement'
            trfpga.perform_time_resolved_measurement()
            print 'now trigger'
            trigger.trigger('PaulBox')
            print 'now get result'
            (arrayLength, timeLength, timeResolution), measuredData = trfpga.get_result_of_measurement()
            measuredData = measuredData.asarray
            infoarray = numpy.array([arrayLength,timeLength,timeResolution])
            saveName = 'freq{0}trace{1}'.format(freq,iteration)
            print 'now saving {}'.format(saveName)
            numpy.savez(saveName,measuredData, infoarray)
            print 'now waiting to complete recooling'
            print time.sleep(0.100)
            
print 'initializing parameters'
initialize()
print 'scanning'
scan()
print 'DONE'




