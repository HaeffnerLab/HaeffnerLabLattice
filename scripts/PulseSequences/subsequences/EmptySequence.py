from scripts.PulseSequences.PulseSequence import PulseSequence

class empty_sequence(PulseSequence):
    
    @classmethod
    def required_parameters(self):
        config = [
                  'empty_sequence_duration'
                  ]
        return config
        
    def sequence(self):
        self.end = self.start + self.empty_sequence_duration