from PulseSequence import PulseSequence
from labrad.units import WithUnit

class sampleDDS(PulseSequence):
    #dictionary of variable: (type, min, max, default)
    def configuration(self):
        config = [
                  ]
        return config
    
    def sequence(self):
        start1 =  WithUnit(10, 'us')
        start2 =  WithUnit(1000, 'ms')
        duration = WithUnit(500, 'ms')
        self.ttl_pulses.append(('crystallization',start1, duration))
        self.ttl_pulses.append(('crystallization',start2, duration))
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    cs = sampleDDS(**{})
    cs.programSequence(cxn.pulser)
    cxn.pulser.start_number(10)
    cxn.pulser.wait_sequence_done()
    cxn.pulser.stop_sequence()
    print 'DONE'