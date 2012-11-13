from lattice.scripts.PulseSequences.PulseSequence import PulseSequence
from labrad.units import WithUnit

class turn_off_all(PulseSequence):
    
    def sequence(self):
        pulses = self.dds_pulses
        dur = WithUnit(50, 'us')
        for channel in ['pump','729DP','110DP','854DP','866DP','radial']:
            pulses.append( (channel, self.start, dur, WithUnit(0, 'MHz'), WithUnit(0, 'dBm')))
        self.end = self.start + dur