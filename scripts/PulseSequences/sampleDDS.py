from PulseSequence import PulseSequence
from labrad import types as T

class sampleDDS(PulseSequence):
    #dictionary of variable: (type, min, max, default)
    def configuration(self):
        config = [
                  ]
        return config
    

    def sequence(self):
        duration = T.Value(3000, 'ms')
        freqs = [T.Value(f, 'MHz') for f in [210.0, 240.0, 230.0]]
        for i,f in enumerate(freqs):
            self.dds_pulses.append( ('729DP',self.start + 2*i*duration + T.Value(10, 'us'), duration, f, T.Value(-3.0, 'dBm')) )
        
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    cs = sampleDDS(**{})
    cs.programSequence(cxn.pulser)
    cxn.pulser.start_number(3)
    cxn.pulser.wait_sequence_done()
    cxn.pulser.stop_sequence()
    print 'DONE'