from lattice.scripts.PulseSequences.PulseSequence import PulseSequence

class optical_pumping_pulsed(PulseSequence):
    
    def configuration(self):
        config = [
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
        return config
    
    def sequence(self):
        cycles = int(self.p.optical_pumping_pulsed_cycles)
        cycle_duration = self.p.optical_pumping_pulsed_duration_729 + self.p.optical_pumping_pulsed_duration_repumps +\
        +self.p.optical_pumping_pulsed_duration_additional_866 + 2 * self.p.optical_pumping_pulsed_duration_between_pulses
        cycles_start = [self.start + cycle_duration * i for i in range(cycles)]
        self.end = self.start + cycles * cycle_duration
        pulses = self.dds_pulses
        freq729 = self.p.optical_pumping_pulsed_frequency_729
        ampl729 = self.p.optical_pumping_pulsed_amplitude_729
        freq866 = self.p.optical_pumping_pulsed_frequency_866
        ampl866 = self.p.optical_pumping_pulsed_amplitude_866
        freq854 = self.p.optical_pumping_pulsed_frequency_854
        ampl854 = self.p.optical_pumping_pulsed_amplitude_854
        for start in cycles_start:
            start_repumps = start + self.p.optical_pumping_pulsed_duration_729 + self.p.optical_pumping_pulsed_duration_between_pulses
            duration_866 =  self.p.optical_pumping_pulsed_duration_repumps + self.p.optical_pumping_pulsed_duration_additional_866
            pulses.append(('729DP', start, self.p.optical_pumping_pulsed_duration_729 , freq729 , ampl729))
            pulses.append(('854DP', start_repumps, self.p.optical_pumping_pulsed_duration_repumps, freq854, ampl854))
            pulses.append(('866DP', start_repumps, duration_866, freq866 , ampl866))