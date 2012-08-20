from scripts.PulseSequences.PulseSequence import PulseSequence

class rabi_excitation(PulseSequence):
    
    @staticmethod
    def configuration():
        config = [
                  'rabi_excitation_frequency',
                  'rabi_excitation_amplitude',
                  'rabi_excitation_duration',
                  ]
        return config
    
    
    def sequence(self):
        pulses = []
        self.end = self.start + self.p.rabi_excitation_duration
        pulses.append((self.start, self.p.rabi_excitation_frequency, self.p.rabi_excitation_amplitude))
        pulses.append((self.end, 0.0, -63.0))
        for pulses in [('729DP', pulses)]:
            self.dds_pulses.append(pulses)