from sequence import Sequence
import time

class TimeResolved(Sequence):
    #dictionary of variable: (type, min, max, default)
    requiredVars = {
                         'recordTime':(float, 10e-9, 5.0, 100e-3)
                    }
    
    def defineSequence(self):
        recordTime = self.vars['recordTime']       
        self.pulser.add_ttl_pulse('TimeResolvedCount', 0.0, recordTime) #record the whole time

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = TimeResolved(pulser)
    pulser.new_sequence()
    params = {
              'recordTime': 0.001
              }
    seq.setVariables(**params)
    seq.defineSequence()
    pulser.program_sequence()
    #print pulser.human_readable().asarray
    pulser.reset_timetags()
    #pulser.start_single()
    #pulser.start_number(1000)
    pulser.start_infinite()
    print 'completed', pulser.repeatitions_completed()
    time.sleep(.5)
    print 'completed', pulser.repeatitions_completed()
    time.sleep(.5)
    print 'completed', pulser.repeatitions_completed()
    #pulser.wait_sequence_done()
    pulser.stop_sequence()
    print 'completed', pulser.repeatitions_completed()
    timetags = pulser.get_timetags().asarray
    print 'measured {0} timetags'.format(timetags.size)