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
        interval = 20
        start_time = 100
        self.dds_pulses.append( ('110DP', WithUnit(start_time, 'us'), WithUnit(interval, 'us'), freq, WithUnit(-13.5, 'dBm')) )
        self.dds_pulses.append( ('110DP', WithUnit(start_time+interval, 'us'), WithUnit(interval, 'us'), freq, WithUnit(-13.0, 'dBm')) )
        self.dds_pulses.append( ('110DP', WithUnit(start_time+2*interval, 'us'), WithUnit(interval, 'us'), freq, WithUnit(-12.5, 'dBm')) )
        self.dds_pulses.append( ('110DP', WithUnit(start_time+3*interval, 'us'), WithUnit(interval, 'us'), freq, WithUnit(-12.0, 'dBm')) )
        self.dds_pulses.append( ('110DP', WithUnit(start_time+4*interval, 'us'), WithUnit(interval, 'us'), freq, WithUnit(-11.5, 'dBm')) )
        self.dds_pulses.append( ('110DP', WithUnit(start_time+5*interval, 'us'), WithUnit(interval, 'us'), freq, WithUnit(-11.0, 'dBm')) )
        self.dds_pulses.append( ('110DP', WithUnit(start_time+6*interval, 'us'), WithUnit(10, 'ms'), freq, WithUnit(-63.0, 'dBm')) )
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    cs = sampleDDS(**{})
    cs.programSequence(cxn.pulser)
    cxn.pulser.start_number(10)
    cxn.pulser.wait_sequence_done()
    cxn.pulser.stop_sequence()
    print 'DONE'