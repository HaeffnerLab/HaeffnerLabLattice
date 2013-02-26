from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence

class repump_d(pulse_sequence):
    
    required_parameters = [
                           ('RepumpD_5_2','repump_d_duration'), 
                           ('RepumpD_5_2','repump_d_frequency_854'), 
                           ('RepumpD_5_2','repump_d_amplitude_854')
                           ]
    
    def sequence(self):
        p = self.parameters.RepumpD_5_2
        self.end = self.start + p.repump_d_duration
        self.addDDS('854DP', self.start, p.repump_d_duration, p.repump_d_frequency_854, p.repump_d_amplitude_854)