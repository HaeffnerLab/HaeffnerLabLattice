from sequence import Sequence
from plotsequence import SequencePlotter
import time
import numpy

class sampleReadout(Sequence):
    #dictionary of variable: (type, min, max, default)
    requiredVars = {
                    }
    

    def defineSequence(self):
        pulser = self.pulser
        pulser.add_ttl_pulse('ReadoutCount', 0.1, 0.001)
        pulser.add_ttl_pulse('ReadoutCount', 0.2, 0.001)
        pulser.add_ttl_pulse('ReadoutCount', 0.3, 0.001)
        pulser.add_ttl_pulse('ReadoutCount', 0.4, 0.01)
        pulser.add_ttl_pulse('ReadoutCount', 0.5, 0.02)
        pulser.add_ttl_pulse('ReadoutCount', 0.6, 0.03)        
        pulser.add_ttl_pulse('ReadoutCount', 0.7, 0.04)   
        pulser.add_ttl_pulse('ReadoutCount', 0.8, 0.05)         
        pulser.add_ttl_pulse('ReadoutCount', 0.9, 0.06)    
        pulser.add_ttl_pulse('ReadoutCount', 1.0, 0.20)            
        pulser.extend_sequence_length(2.0)
        
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = sampleReadout(pulser)
    pulser.new_sequence()
    seq.defineSequence()
    pulser.program_sequence()
    #pulser.reset_readout_counts()
    pulser.start_single()
    pulser.wait_sequence_done()
    pulser.stop_sequence()
    counts = pulser.get_readout_counts().asarray
    print counts
    print 'done'