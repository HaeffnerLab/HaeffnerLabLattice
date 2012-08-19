from scripts.PulseSequences.PulseSequence import PulseSequence

class EmptySequence(PulseSequence):
      
    def configuration(self):
        config = [
                  'duration'
                  ]
        return config
        
    def sequence(self):
        self.end = self.start + self.p.duration