from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class SZX(pulse_sequence):
    
    
    def sequence(self):

    	p = self.parameters.SZX