from scripts.PulseSequences.PulseSequence import PulseSequence
from labrad import types as T

class turn_off_all(PulseSequence):
    
    def sequence(self):
        pulses = self.dds_pulses
        dur = T.Value(100, 'us')
        pulses.append( ('pump', self.start, dur, T.Value(110, 'MHz'), T.Value(-3, 'dBm')))
        self.end = self.start + dur