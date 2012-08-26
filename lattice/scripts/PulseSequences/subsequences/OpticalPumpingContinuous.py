from scripts.PulseSequences.PulseSequence import PulseSequence

class optical_pumping_continuous(PulseSequence):
    
    def configuration(self):
        config = [
                  'optical_pumping_continuous_duration',
                  'optical_pumping_continuous_repump_additional',
                  'optical_pumping_continuous_frequency_854',
                  'optical_pumping_continuous_amplitude_854',
                  'optical_pumping_continuous_frequency_729',
                  'optical_pumping_continuous_amplitude_729',
                  ]
        return config
    
    
    def sequence(self):
        repump_dur = self.p.optical_pumping_continuous_duration + self.p.optical_pumping_continuous_repump_additional
        pulses = self.dds_pulses
        self.end = self.start + self.p.optical_pumping_continuous_duration + self.p.optical_pumping_continuous_repump_additional
        pulses.append(('729DP', self.start, self.p.optical_pumping_continuous_duration, self.p.optical_pumping_continuous_frequency_729, self.p.optical_pumping_continuous_amplitude_729))
        pulses.append(('854DP', self.start, repump_dur, self.p.optical_pumping_continuous_frequency_854, self.p.optical_pumping_continuous_amplitude_854))
        pulses.append(('866DP', self.start, repump_dur, self.p.optical_pumping_continuous_frequency_854, self.p.optical_pumping_continuous_amplitude_854))