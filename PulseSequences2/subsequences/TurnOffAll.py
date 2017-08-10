from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class TurnOffAll(pulse_sequence):
    
    def sequence(self):
        dur = WithUnit(1000, 'us')
        for channel in ['729global', '729local','397','854','866','radial']:
            self.addDDS(channel, self.start, dur, WithUnit(0, 'MHz'), WithUnit(0, 'dBm') )
        self.end = self.start + dur