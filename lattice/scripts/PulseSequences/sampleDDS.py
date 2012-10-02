from PulseSequence import PulseSequence
from labrad import types as T

class sampleDDS(PulseSequence):
    #dictionary of variable: (type, min, max, default)
    def configuration(self):
        config = [
                  ]
        return config
    

    def sequence(self):
        duration = T.Value(10, 'ms')
        self.dds_pulses.append( ('866DP',self.start + T.Value(10, 'us'), T.Value(10, 'ms'), T.Value(80, 'MHz'), T.Value(-3.0, 'dBm')) )
        self.dds_pulses.append( ('110DP',self.start + T.Value(10, 'us'), 2* T.Value(10, 'ms'), T.Value(110, 'MHz'), T.Value(-11.0, 'dBm')) )
        self.end = self.start + 2 * duration
        
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    cs = sampleDDS(**{})
    cs.programSequence(cxn.pulser)
    cxn.pulser.start_number(1000)
    cxn.pulser.wait_sequence_done()
    cxn.pulser.stop_sequence()
    print 'DONE'