from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class EmptySequence(pulse_sequence):
    
    
  
    def sequence(self):
        
        duration=self.parameters.EmptySequence.empty_sequence_duration
        
        # if duration > WithUnit(2.0, 'us'):
        #     # turn on the modulation of the 397 without any modulation will cause the 397 to disable the switch and add 
        #     # another -40dbm attenuation from the switch
        #     self.addTTL('397mod', self.start , duration )
            
        self.end = self.start + duration
        #self.end = self.start + self.parameters.EmptySequence.empty_sequence_duration