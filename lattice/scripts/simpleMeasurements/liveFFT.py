import os; labradPath = os.environ.get('LABRADPATH') 
path = os.path.join(labradPath,'lattice/scripts')
import sys; sys.path.append(path)
import labrad; cxn = labrad.connect()
from scriptLibrary import paulsbox 

iterations = 1
#program pulse sequence for triggering time resolved
pboxDict = {
            'sequence':'TimeResolvedTrigger.py',
            'nothing':1,
            }
paulsbox.program(cxn.paul_box, pboxDict)
recordTime = 0.33554432 
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
    (arrayLength, timeLength, timeResolution), measuredData = trfpga.get_result_of_measurement()
    measuredData = measuredData.asarray
    if not dpInputSet:
        dp.set_inputs('timeResolvedFFT',[('uncompressedArrByteLength',arrayLength),('resolution',timeResolution)])
        dp.new_process('timeResolvedFFT')
        dpInputSet = True
    dp.process_new_data('timeResolvedFFT', measuredData)
    dp.get_result('timeResolvedFFT')
    


