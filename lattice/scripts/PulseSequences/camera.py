from sequence import Sequence
import time

class Camera(Sequence):
    #dictionary of variable: (type, min, max, default)
    requiredVars = {
                         'iterations':(int, 1, 1000, 1),
                         'period':(float, 100e-9, 5.0, 0.1)
                    }
    
    def defineSequence(self):
        pulser = self.pulser
        p = self.parameters
        
        for i in range(p.iterations):
            print i*p.period  
            self.pulser.add_ttl_pulse('camera', (i*p.period), 10e-6) #record the whole time

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = Camera(pulser)
    #pulser.switch_auto('camera',  True)
    pulser.new_sequence()
    params = {
              'iterations': 90,
              'period': .2,
              }
    seq.setVariables(**params)
    seq.defineSequence()
    pulser.program_sequence()
    t1 = time.clock()
    pulser.start_single()
    pulser.wait_sequence_done(40)
    pulser.stop_sequence()
    t2 = time.clock()
    print 'done, time it took:', (t2 - t1)