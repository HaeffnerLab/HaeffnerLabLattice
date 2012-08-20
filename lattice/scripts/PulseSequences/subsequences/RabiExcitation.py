from scripts.PulseSequences.PulseSequence import PulseSequence
from labrad import types as T

class rabi_excitation(PulseSequence):
    
    def configuration(self):
        config = [
                  'rabi_excitation_frequency',
                  'rabi_excitation_amplitude',
                  'rabi_excitation_duration',
                  ]
        return config
    
    
    def sequence(self):
        pulses = []
        if self.p.rabi_excitation_duration.value == 0:
            return
        self.end = self.start + self.p.rabi_excitation_duration
        pulses.append((self.start, self.p.rabi_excitation_frequency, self.p.rabi_excitation_amplitude))
        pulses.append((self.end, T.Value(0.0, 'MHz'), T.Value(-63.0, 'dBm')))
        for pulses in [('729DP', pulses)]:
            self.dds_pulses.append(pulses)