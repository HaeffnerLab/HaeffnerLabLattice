import os; labradPath = os.environ.get('LABRADPATH') 
path = os.path.join(labradPath,'lattice/scripts')
import sys; sys.path.append(path)
import labrad; cxn = labrad.connect()
from scriptLibrary import paulsbox 
import time

iterations = 1
#program pulse sequence for triggering time resolved
pboxDict = {
            'sequence':'TimeResolvedTrigger.py',
            'nothing':1,
            }
paulsbox.program(cxn.paul_box, pboxDict)
recordTime = 0.33554432
#0.02097152
#0.04194304
#0.04194304
#0.33554432 
#0.16777216
#0.02097152 
#0.33554432 
#0.16777216 #in seconds
#0.02097152


trfpga = cxn.timeresolvedfpga
dp = cxn.dataprocessor
trigger = cxn.trigger
trfpga.set_time_length(recordTime)
dpInputSet = False

for iteration in range(iterations):
    print 'iteration', iteration
    trfpga.perform_time_resolved_measurement()
    print 'now trigger'
    trigger.trigger('PaulBox')
    print 'now get result'
    t1 = time.time()
    (arrayLength, timeLength, timeResolution), measuredData = trfpga.get_result_of_measurement()
    print 'measurement took', time.time() - t1
    measuredData = measuredData.asarray
        if not dpInputSet:
        dp.set_inputs('timeResolvedFFTselected',[('uncompressedArrByteLength',arrayLength),('resolution',timeResolution),('needFrequency',14.99886*10**6),('AvgPointSide',10)])
        dp.new_process('timeResolvedFFTselected')
        dpInputSet = True
    print 'adding data'
    t1 = time.time()
    dp.process_new_data('timeResolvedFFTselected', measuredData)
    print 'getting result'
    result = dp.get_result('timeResolvedFFTselected')
    print 'result', result
    print 'processing took', time.time() - t1


