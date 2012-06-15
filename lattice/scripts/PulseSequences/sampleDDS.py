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
        pulser.add_dds_pulses('866DP', [(100e-9, 65.0 , -33.0)])
        pulser.add_dds_pulses('866DP', [(.1 + 100e-9, 70.0 , -33.0)])
        pulser.add_dds_pulses('866DP', [(.2 + 100e-9, 75.0 , -33.0)])
        pulser.add_dds_pulses('866DP', [(.3 + 100e-9, 80.0 , -33.0)])
        pulser.add_dds_pulses('axial', [(100e-9, 95.0 , -3.0)])
        pulser.add_dds_pulses('axial', [(.1 + 100e-9, 90.0 , -3.0)])
        pulser.add_dds_pulses('axial', [(.2 + 100e-9, 85.0 , -3.0)])
        pulser.add_dds_pulses('854DP', [(100e-9, 95.0 + 5, -13.0)])
        pulser.add_dds_pulses('854DP', [(.1 + 100e-9, 90.0 + 5 , -13.0)])
        pulser.add_dds_pulses('854DP', [(.2 + 100e-9, 85.0 + 5 , -13.0)])
        pulser.add_dds_pulses('110DP', [(100e-9, 60.0 , -23.0)])
        pulser.add_dds_pulses('110DP', [(.1 + 100e-9, 65.0 , -23.0)])
        pulser.add_dds_pulses('110DP', [(.2 + 100e-9, 70.0 , -23.0)])
        pulser.add_dds_pulses('110DP', [(.3 + 100e-9, 75.0 , -23.0)])
        
        
        pulser.extend_sequence_length(0.5)
            
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = sampleDDS(pulser)
    pulser.new_sequence()
    seq.defineSequence()
    pulser.program_sequence()
#    pulser.start_single()
    pulser.start_number(100)
    #time.sleep(2)
    pulser.wait_sequence_done(1000.0)
    #print 'completed', pulser.repeatitions_completed()
    pulser.stop_sequence()
    #print 'completed', pulser.repeatitions_completed()
#    hr = pulser.human_readable().asarray
#    channels = pulser.get_channels().asarray
#    sp = SequencePlotter(hr, channels)
#    sp.makePlot()
    print 'done'