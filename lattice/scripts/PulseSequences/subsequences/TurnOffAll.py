from scripts.PulseSequences.PulseSequence import PulseSequence
from labrad import types as T

class turn_off_all(PulseSequence):
    
    def sequence(self):
        pulses = self.dds_pulses
        dur = T.Value(50, 'us')
        for channel in ['pump','729DP','110DP','854DP','866DP']:
            pulses.append( (channel, self.start, dur, T.Value(0, 'MHz'), T.Value(0, 'dBm')))
        self.end = self.start + dur