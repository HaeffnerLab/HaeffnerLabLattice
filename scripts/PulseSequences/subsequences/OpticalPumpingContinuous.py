from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence

class optical_pumping_continuous(pulse_sequence):
    
    @classmethod
    def required_parameters(cls):
        config = [
                  'optical_pumping_continuous_duration',
                  'optical_pumping_continuous_repump_additional',
                  'optical_pumping_continuous_frequency_854',
                  'optical_pumping_continuous_amplitude_854',
                  'optical_pumping_continuous_frequency_729',
                  'optical_pumping_continuous_amplitude_729',
                  'optical_pumping_continuous_frequency_866', 
                  'optical_pumping_continuous_amplitude_866',
                  ]
        return config
    
    def sequence(self):
        repump_dur_854 = self.optical_pumping_continuous_duration + self.optical_pumping_continuous_repump_additional
        repump_dur_866 = self.optical_pumping_continuous_duration + 2 * self.optical_pumping_continuous_repump_additional
        pulses = self.dds_pulses
        self.end = self.start + repump_dur_866
        pulses.append(('729DP', self.start, self.optical_pumping_continuous_duration, self.optical_pumping_continuous_frequency_729, self.optical_pumping_continuous_amplitude_729))
        pulses.append(('854DP', self.start, repump_dur_854, self.optical_pumping_continuous_frequency_854, self.optical_pumping_continuous_amplitude_854))
        pulses.append(('866DP', self.start, repump_dur_866, self.optical_pumping_continuous_frequency_866, self.optical_pumping_continuous_amplitude_866))