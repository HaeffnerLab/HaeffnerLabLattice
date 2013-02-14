from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class turn_off_all(pulse_sequence):
    
    def sequence(self):
        dur = WithUnit(50, 'us')
        for channel in ['pump','729DP','110DP','854DP','866DP','radial']:
            self.addDDS(channel, self.start, dur, WithUnit(0, 'MHz'), WithUnit(0, 'dBm') )
        self.end = self.start + dur