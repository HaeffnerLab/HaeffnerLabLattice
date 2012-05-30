from sequence import Sequence
import time

class sampleDDS(Sequence):
    #dictionary of variable: (type, min, max, default)
    requiredVars = {
                         'recordTime':(float, 10e-9, 5.0, 100e-3)
                    }
    
    def defineSequence(self):
        pulser = self.pulser
        p = self.parameters
        
        #pulser.add_ttl_pulse('TimeResolvedCount', 0.0, p.recordTime) #record the whole time
        pulser.add_dds_pulses('110DP', [(0.1, 100.0, -63.0)])
        pulser.add_dds_pulses('110DP', [(0.2, 120.0, -63.0)])
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = sampleDDS(pulser)
    pulser.new_sequence()
    params = {
              'recordTime': 0.100
              }
    seq.setVariables(**params)
    seq.defineSequence()
    pulser.program_sequence()
    pulser.start_single()
    pulser.wait_sequence_done()
    pulser.stop_sequence()