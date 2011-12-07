import os; labradPath = os.environ.get('LABRADPATH') 
path = os.path.join(labradPath,'lattice/scripts')
import sys; sys.path.append(path)
import labrad; cxn = labrad.connect()
from scriptLibrary import paulsbox 

#program pulse sequence for triggering time resolved
pboxDict = {
            'sequence':'TimeResolvedTrigger.py',
            'nothing':1,
            }
paulsbox.program(cxn.paul_box, pboxDict)
recordTime = 0.5

trfpga = cxn.timeresolvedfpga
trigger = cxn.trigger
trfpga.set_time_length(recordTime)
trfpga.perform_time_resolved_measurement()
trigger.trigger('PaulBox')
tags = trfpga.get_result_of_measurement().asarray
count = tags.shape[0]
print 'in {} sec received {} photons'.format(recordTime, count)

