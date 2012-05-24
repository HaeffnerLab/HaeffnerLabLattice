from sequence import Sequence
import time

class Camera(Sequence):
    #dictionary of variable: (type, min, max, default)
    requiredVars = {
                         'iterations':(int, 1, 1000, 1),
                         'period':(float, 100e-9, 1.0, 0.1)
                    }
    
    def defineSequence(self):
        pulser = self.pulser
        p = self.parameters
        
        for i in range(p.iterations):  
            self.pulser.add_ttl_pulse('camera', 0.0, recordTime) #record the whole time

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = Camera(pulser)
    pulser.new_sequence()
    params = {
              'recordTime': 0.001,
              'iterations':1,
              }
    seq.setVariables(**params)
    seq.defineSequence()
    pulser.program_sequence()
    pulser.start_single()
    pulser.wait_sequence_done()
    pulser.stop_sequence()
    print 'done'