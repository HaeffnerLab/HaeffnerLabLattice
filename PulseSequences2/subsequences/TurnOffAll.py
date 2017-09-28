from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class TurnOffAll(pulse_sequence):
    
    def sequence(self):
        dur = WithUnit(50, 'us')
        for channel in ['729global', '729local','397','854','866','radial']:
            self.addDDS(channel, self.start, dur, WithUnit(0, 'MHz'), WithUnit(-63., 'dBm') )
        
        # changing the 866 from a dds to a rf source enabled by a switch
        #self.addTTL('866DP', self.start, repump_dur_866 )
        
        self.end = self.start + dur