import labrad
import numpy
import time
import os
#global parameters
##Frequency Scan of Local Heating Beam
MIN_FREQ = 190.0 #MHZ####
MAX_FREQ = 250.0 #MHZ
STEP_FREQ = 15#MHZ
FreqScanList = numpy.arange(MIN_FREQ,MAX_FREQ + STEP_FREQ, STEP_FREQ)
##Timing for Paul's Box Sequence, all in microseconds
pboxSequence = 'LocalHeatingLineScan.py' 
backgroundMeasureTime = 20.*10**3 #microseconds
localHeatingTime = 50.*10**3#microseconds
recoolingTime = 50.*10**3 #microseconds
iterationsPerFreq = 100#### #how many traces to take at each frequency
recordTime =  (backgroundMeasureTime + localHeatingTime + recoolingTime) / 10**6 #in seconds
#data processing on the fly
binTime =50*10**-6
#connect
cxn = labrad.connect()
#define servers we'll be using
dv = cxn.data_vault
sigGen = cxn.rohdeschwarz_server
sigGen.select_device('lattice-pc GPIB Bus - USB0::0x0AAD::0x0054::104543')
trigger = cxn.trigger
pbox = cxn.paul_box
trfpga = cxn.timeresolvedfpga
dp = cxn.dataprocessor

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
    #get calibration
    dv.cd(['','Calibrations'],True)
    dv.open(62)
    calibration = dv.get().asarray
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
    dirappend = time.asctime().replace(' ','').replace(':','')
    directory = os.getcwd() + '\\' + dirappend
    os.mkdir(directory)
    os.chdir(directory)
    #set dataprocessing inputs
    resolution = trfpga.get_resolution()
    dp.set_inputs('timeResolvedBinning',[('timelength',recordTime),('resolution',resolution),('bintime',binTime)])
    #where to save into datavault
    dv.cd(['','Experiments', 'localheatinglinescan',dirappend], True )
    return calibration####
    
def scan(calibration):####
   #for freq in FreqScanList:
    for point in calibration[1:40:7]:
        freq = point[0]
        power = point[1]
        print 'setting frequency {}'.format(freq)
        sigGen.frequency(freq)
        #print 'setting power {}'.format(power)
        #sigGen.amplitude(power)####
        dp.new_process('timeResolvedBinning')
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
            print 'now adding to dataprocessing server'
            dp.process_new_data('timeResolvedBinning',measuredData)
            print 'now waiting to complete recooling'
            print time.sleep(0.100)
        print 'getting result and adding to data vault'
        binned = dp.get_result('timeResolvedBinning').asarray
        dv.new('binnedFlourescence',[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
        dv.add(binned)
        
print 'initializing parameters'
calibration = initialize()
print 'scanning'
scan(calibration)
print 'DONE'




