from sequence import Sequence
from plotsequence import SequencePlotter
import time
import numpy

class sampleDDS(Sequence):
    #dictionary of variable: (type, min, max, default)
    requiredVars = {
                    }
    

    def defineSequence(self):
        pulser = self.pulser
        #pulser.add_ttl_pulse('AdvanceDDS', 200e-3, 10e-6)
        pulser.add_ttl_pulse('ResetDDS', 200e-3, 10e-6)
        
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = sampleDDS(pulser)
    pulser.new_sequence()
    seq.defineSequence()
    pulser.program_sequence()
    pulser.start_single()
    pulser.wait_sequence_done()
    pulser.stop_sequence()
    print 'done'