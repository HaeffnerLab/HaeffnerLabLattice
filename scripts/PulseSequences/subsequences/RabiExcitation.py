from lattice.scripts.PulseSequences.PulseSequence import PulseSequence

class rabi_excitation(PulseSequence):
    
    def configuration(self):
        config = [
                  'rabi_excitation_frequency',
                  'rabi_excitation_amplitude',
                  'rabi_excitation_duration',
                  ]
        return config
    
    
    def sequence(self):
        self.end = self.start + self.p.rabi_excitation_duration
        #from labrad import types as T
        #self.p.rabi_excitation_duration = T.Value(100,'s')
        self.dds_pulses.append(('729DP', self.start, self.p.rabi_excitation_duration, self.p.rabi_excitation_frequency, self.p.rabi_excitation_amplitude))