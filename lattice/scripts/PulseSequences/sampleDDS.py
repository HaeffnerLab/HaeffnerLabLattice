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
        p = self.parameters
        pulser.add_dds_pulses('866DP', [(40e-9, 80.0 , -3.0)])
        pulser.add_dds_pulses('110DP', [(40e-9, 110.0 , -63.0)])
        pulser.add_dds_pulses('866DP', [(1.1, 80.0 , -63.0)])
        pulser.add_dds_pulses('110DP', [(1.1, 110.0 , -3.0)])
        pulser.add_dds_pulses('866DP', [(2.1, 80.0 , -3.0)])
        pulser.add_dds_pulses('110DP', [(2.1, 110.0 , -63.0)])
        pulser.extend_sequence_length(3.1)
            
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = sampleDDS(pulser)
    pulser.new_sequence()
    seq.defineSequence()
    pulser.program_sequence()
    pulser.start_single()
    #pulser.start_number(100)
    #time.sleep(2)
    pulser.wait_sequence_done(10.0)
    #print 'completed', pulser.repeatitions_completed()
    pulser.stop_sequence()
    #print 'completed', pulser.repeatitions_completed()
#    hr = pulser.human_readable().asarray
#    channels = pulser.get_channels().asarray
#    sp = SequencePlotter(hr, channels)
#    sp.makePlot()