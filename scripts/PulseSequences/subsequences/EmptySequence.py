from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence

class empty_sequence(pulse_sequence):
    
    
    required_parameters =  [('EmptySequence','empty_sequence_duration')]

    def sequence(self):
        self.end = self.start + self.parameters.EmptySequence.empty_sequence_duration