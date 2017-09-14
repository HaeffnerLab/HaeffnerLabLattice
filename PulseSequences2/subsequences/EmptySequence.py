from common.devel.bum.sequences.pulse_sequence import pulse_sequence

class EmptySequence(pulse_sequence):
    
    
  
    def sequence(self):

        self.end = self.start + self.parameters.EmptySequence.empty_sequence_duration