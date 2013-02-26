from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence

class optical_pumping_pulsed(pulse_sequence):
    
    required_parameters =   [
                          ('OpticalPumpingPulsed','optical_pumping_pulsed_cycles'),
                          ('OpticalPumpingPulsed','optical_pumping_pulsed_duration_729'),
                          ('OpticalPumpingPulsed','optical_pumping_pulsed_duration_repumps'),
                          ('OpticalPumpingPulsed','optical_pumping_pulsed_duration_additional_866'),
                          ('OpticalPumpingPulsed','optical_pumping_pulsed_duration_between_pulses'),
                          ('OpticalPumpingPulsed','optical_pumping_pulsed_frequency_854'),
                          ('OpticalPumpingPulsed','optical_pumping_pulsed_amplitude_854'),
                          ('OpticalPumpingPulsed','optical_pumping_pulsed_frequency_729'),
                          ('OpticalPumpingPulsed','optical_pumping_pulsed_amplitude_729'),
                          ('OpticalPumpingPulsed','optical_pumping_pulsed_frequency_866'), 
                          ('OpticalPumpingPulsed','optical_pumping_pulsed_amplitude_866'),
                          ]
    
    def sequence(self):
        opp = self.parameters.OpticalPumpingPulsed
        cycles = int(opp.optical_pumping_pulsed_cycles)
        cycle_duration = opp.optical_pumping_pulsed_duration_729 + opp.optical_pumping_pulsed_duration_repumps +\
        +opp.optical_pumping_pulsed_duration_additional_866 + 2 * opp.optical_pumping_pulsed_duration_between_pulses
        cycles_start = [self.start + cycle_duration * i for i in range(cycles)]
        self.end = self.start + cycles * cycle_duration
        freq729 = opp.optical_pumping_pulsed_frequency_729
        ampl729 = opp.optical_pumping_pulsed_amplitude_729
        freq866 = opp.optical_pumping_pulsed_frequency_866
        ampl866 = opp.optical_pumping_pulsed_amplitude_866
        freq854 = opp.optical_pumping_pulsed_frequency_854
        ampl854 = opp.optical_pumping_pulsed_amplitude_854
        for start in cycles_start:
            start_repumps = start + opp.optical_pumping_pulsed_duration_729 + opp.optical_pumping_pulsed_duration_between_pulses
            duration_866 =  opp.optical_pumping_pulsed_duration_repumps + opp.optical_pumping_pulsed_duration_additional_866
            self.addDDS('729', start, opp.optical_pumping_pulsed_duration_729 , freq729 , ampl729)
            self.addDDS('854', start_repumps, opp.optical_pumping_pulsed_duration_repumps, freq854, ampl854)
            self.addDDS('866', start_repumps, duration_866, freq866 , ampl866)