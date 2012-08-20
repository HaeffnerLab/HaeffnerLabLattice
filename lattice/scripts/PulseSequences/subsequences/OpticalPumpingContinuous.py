from scripts.PulseSequences.PulseSequence import PulseSequence
from labrad import types as T

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
        pulses729 = []
        pulses854 = []
        self.end = self.start + self.p.optical_pumping_continuous_duration + self.p.optical_pumping_continuous_repump_additional
        self.end729 = self.start + self.p.optical_pumping_continuous_duration
        pulses729.append((self.start, self.p.optical_pumping_continuous_frequency_729, self.p.optical_pumping_continuous_amplitude_729))
        pulses729.append((self.end729, T.Value(0.0, 'MHz'), T.Value(-63.0, 'dBm')))
        pulses854.append((self.start, self.p.optical_pumping_continuous_frequency_854, self.p.optical_pumping_continuous_amplitude_854))
        pulses854.append((self.end, self.p.optical_pumping_continuous_frequency_854, T.Value(-63.0, 'dBm')))
        for pulses in [('854DP', pulses854),('729DP', pulses729)]:
            self.dds_pulses.append(pulses)