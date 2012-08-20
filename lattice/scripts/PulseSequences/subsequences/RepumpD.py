from scripts.PulseSequences.PulseSequence import PulseSequence

class repump_d(PulseSequence):
    
    def configuration(self):
        config = [
                  'repump_d_duration',
                  'repump_d_frequency_854',
                  'repump_d_amplitude_854',
                  ]
        return config
    
    def sequence(self):
        pulses854 = []
        self.end = self.start + self.p.repump_d_duration
        pulses854.append((self.start, self.p.repump_d_frequency_854, self.p.repump_d_amplitude_854))
        pulses854.append((self.end, self.p.repump_d_frequency_854, -63.0))
        for pulses in [('854DP', pulses854)]:
            self.dds_pulses.append(pulses)