from scripts.PulseSequences.SemaphoreSequence import SemaphoreSequence
from labrad import types as T

class EmptySequence(SemaphoreSequence):
      
    def user_configuration(self):
        config = {
                  'duration':[T.Value(0.0, 's'), T.Value(50.0, 's'), T.Value(0.0, 's')]
                  }
        return config
        
    def sequence(self):
        self.end = self.start + self.p.duration