from PulseSequence import PulseSequence
from labrad.units import WithUnit

class sampleDDS(PulseSequence):
    #dictionary of variable: (type, min, max, default)
    def configuration(self):
        config = [
                  ]
        return config
    
    def sequence(self):
        freq = WithUnit(110.0, 'MHz')
        self.dds_pulses.append( ('110DP', WithUnit(10, 'us'), WithUnit(5, 'us'), freq, WithUnit(-61.0, 'dBm')) )
        self.dds_pulses.append( ('110DP', WithUnit(15, 'us'), WithUnit(5, 'us'), freq, WithUnit(-51.0, 'dBm')) )
        self.dds_pulses.append( ('110DP', WithUnit(20, 'us'), WithUnit(5, 'us'), freq, WithUnit(-41.0, 'dBm')) )
        self.dds_pulses.append( ('110DP', WithUnit(25, 'us'), WithUnit(5, 'us'), freq, WithUnit(-31.0, 'dBm')) )
        self.dds_pulses.append( ('110DP', WithUnit(30, 'us'), WithUnit(5, 'us'), freq, WithUnit(-21.0, 'dBm')) )
        self.dds_pulses.append( ('110DP', WithUnit(35, 'us'), WithUnit(200, 'us'), freq, WithUnit(-11.0, 'dBm')) )
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    cs = sampleDDS(**{})
    cs.programSequence(cxn.pulser)
    cxn.pulser.start_number(10)
    cxn.pulser.wait_sequence_done()
    cxn.pulser.stop_sequence()
    print 'DONE'