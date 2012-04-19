from sequence import Sequence
import time

class thermalization(Sequence):
    #dictionary of variable: (type, min, max, default)
    requiredVars = {
                         'probe_on':(float, 10e-9, 5.0, 100e-3),
                    }
    
    def defineSequence(self):
        probe_on = self.vars['probe_on']
        self.pulser.add_ttl_pulse('axial', 0.0, probe_on)
        self.pulser.add_ttl_pulse('TimeResolvedCount', 0.0, probe_on)
        self.pulser.add_ttl_pulse('866DP', 0.0, probe_on)
            
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = thermalization(pulser)
    pulser.new_sequence()
    params = {
              'probe_on':1e-6,
              }
    seq.setVariables(**params)
    seq.defineSequence()
    pulser.program_sequence()
    pulser.reset_timetags()
    pulser.start_single()
    pulser.wait_sequence_done()
    pulser.stop_sequence()
    timetags = pulser.get_timetags().asarray
    print 'got {} timetags'.format(timetags.size)