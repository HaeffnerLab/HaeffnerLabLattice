from lattice.scripts.PulseSequences.PulseSequence import PulseSequence

class repump_d(PulseSequence):

    def configuration(self):
        config = [
                  'repump_d_duration',
                  'repump_d_frequency_854',
                  'repump_d_amplitude_854',
                  ]
        return config
    
    def sequence(self):
        self.end = self.start + self.p.repump_d_duration
        pulse = ('854DP', self.start, self.p.repump_d_duration, self.p.repump_d_frequency_854, self.p.repump_d_amplitude_854)
        self.dds_pulses.append(pulse)