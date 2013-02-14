from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence

class optical_pumping_pulsed(pulse_sequence):
    
    required_parameters =   [
                          'optical_pumping_pulsed_cycles',
                          'optical_pumping_pulsed_duration_729',
                          'optical_pumping_pulsed_duration_repumps',
                          'optical_pumping_pulsed_duration_additional_866',
                          'optical_pumping_pulsed_duration_between_pulses',
                          'optical_pumping_pulsed_frequency_854',
                          'optical_pumping_pulsed_amplitude_854',
                          'optical_pumping_pulsed_frequency_729',
                          'optical_pumping_pulsed_amplitude_729',
                          'optical_pumping_pulsed_frequency_866', 
                          'optical_pumping_pulsed_amplitude_866',
                          ]
    
    def sequence(self):
        cycles = int(self.optical_pumping_pulsed_cycles)
        cycle_duration = self.optical_pumping_pulsed_duration_729 + self.optical_pumping_pulsed_duration_repumps +\
        +self.optical_pumping_pulsed_duration_additional_866 + 2 * self.optical_pumping_pulsed_duration_between_pulses
        cycles_start = [self.start + cycle_duration * i for i in range(cycles)]
        self.end = self.start + cycles * cycle_duration
        freq729 = self.optical_pumping_pulsed_frequency_729
        ampl729 = self.optical_pumping_pulsed_amplitude_729
        freq866 = self.optical_pumping_pulsed_frequency_866
        ampl866 = self.optical_pumping_pulsed_amplitude_866
        freq854 = self.optical_pumping_pulsed_frequency_854
        ampl854 = self.optical_pumping_pulsed_amplitude_854
        for start in cycles_start:
            start_repumps = start + self.optical_pumping_pulsed_duration_729 + self.optical_pumping_pulsed_duration_between_pulses
            duration_866 =  self.optical_pumping_pulsed_duration_repumps + self.optical_pumping_pulsed_duration_additional_866
            self.addDDS('729DP', start, self.optical_pumping_pulsed_duration_729 , freq729 , ampl729)
            self.addDDS('854DP', start_repumps, self.optical_pumping_pulsed_duration_repumps, freq854, ampl854)
            self.addDDS('866DP', start_repumps, duration_866, freq866 , ampl866)