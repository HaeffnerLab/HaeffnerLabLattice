from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence

class empty_sequence(pulse_sequence):
    
    @classmethod
    def required_parameters(cls):
        config = [
                  'empty_sequence_duration'
                  ]
        return config
        
    def sequence(self):
        self.end = self.start + self.empty_sequence_duration