from sequence import Sequence
from labrad import types as T

class TimeResolved(Sequence):
    #dictionary of variable: (type, min, max, default)
    requiredVars = {
                         'recordTime':(float, 10e-9, 5.0, 100e-3)
                    }
    
    def defineSequence(self):
        recordTime = self.vars['recordTime']       
        self.pulser.add_ttl_pulse('TimeResolvedCount', T.Value(0.0,'s'), T.Value(recordTime,'s')) #record the whole time

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = TimeResolved(pulser)
    pulser.new_sequence()
    params = {
              'recordTime': 0.100
              }
    seq.setVariables(**params)
    seq.defineSequence()
    pulser.program_sequence()
    pulser.reset_timetags()
    pulser.start_number(1)
    pulser.wait_sequence_done()
    pulser.stop_sequence()
    print 'completed', pulser.repeatitions_completed()
    timetags = pulser.get_timetags().asarray
    print timetags
    print 'measured {0} timetags'.format(timetags.size)