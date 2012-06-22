from sequence import Sequence
import time
import numpy as np

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
              'recordTime': 0.15
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
    print timetags[0:249]
    counts = []
    print 'measured {0} timetags'.format(timetags.size)
    ix = np.where(np.ediff1d(timetags) < 0 )[0] #when the next sequence starts, timetags decrease
    split = np.split(timetags, ix + 1)
    if len(split) > 1:
        print 'num split',len(split)
        print 'error'
        for iter in range(len(split)):
            if iter + 1 < len(split):
                print round(10**9 * (split[iter + 1][0] - split[iter][-1]))
#    for iter,sp in enumerate(split):
#        print sp
#        counts.append(sp.size)
#        if sp.size < 20 and iter > 1 and iter < 500:
#            print 'FOUND!'
#            print split[iter-1]
#            print sp.size, sp
#            print split[iter+1]
#            print 'conesectuve differences'
#            print split[iter+1][0] - sp[-1]
#            print sp[0] - split[iter-1][-1]