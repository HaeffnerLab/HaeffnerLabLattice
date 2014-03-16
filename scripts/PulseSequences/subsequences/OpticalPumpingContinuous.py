from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence

class optical_pumping_continuous(pulse_sequence):
    
    
    required_parameters = [
                  ('OpticalPumpingContinuous','optical_pumping_continuous_duration'),
                  ('OpticalPumpingContinuous','optical_pumping_continuous_repump_additional'),
                  ('OpticalPumpingContinuous','optical_pumping_continuous_frequency_854'),
                  ('OpticalPumpingContinuous','optical_pumping_continuous_amplitude_854'),
                  ('OpticalPumpingContinuous','optical_pumping_continuous_frequency_729'),
                  ('OpticalPumpingContinuous','optical_pumping_continuous_amplitude_729'),
                  ('OpticalPumpingContinuous','optical_pumping_continuous_frequency_866'), 
                  ('OpticalPumpingContinuous','optical_pumping_continuous_amplitude_866'),
                  
                  ('OpticalPumpingAux','aux_op_enable'),
                  ('OpticalPumpingAux','aux_optical_pumping_amplitude_729'),
                  ('OpticalPumpingAux','aux_optical_frequency_729'),
                  ]

    def sequence(self):
        opc = self.parameters.OpticalPumpingContinuous
        repump_dur_854 = opc.optical_pumping_continuous_duration + opc.optical_pumping_continuous_repump_additional
        repump_dur_866 = opc.optical_pumping_continuous_duration + 2 * opc.optical_pumping_continuous_repump_additional
        self.end = self.start + repump_dur_866
        self.addDDS('729', self.start, opc.optical_pumping_continuous_duration, opc.optical_pumping_continuous_frequency_729, opc.optical_pumping_continuous_amplitude_729)
        print 'op:', opc.optical_pumping_continuous_frequency_729
        self.addDDS('854', self.start, repump_dur_854, opc.optical_pumping_continuous_frequency_854, opc.optical_pumping_continuous_amplitude_854)
        self.addDDS('866', self.start, repump_dur_866, opc.optical_pumping_continuous_frequency_866, opc.optical_pumping_continuous_amplitude_866)
        aux = self.parameters.OpticalPumpingAux
        if aux.aux_op_enable:
            self.addDDS('729DP_aux', self.start, opc.optical_pumping_continuous_duration, aux.aux_optical_frequency_729, aux.aux_optical_pumping_amplitude_729)
            print 'aux op:', aux.aux_optical_frequency_729
# class optical_pumping_continuous(pulse_sequence):
#     
#     
#     required_parameters = [
#                   ('OpticalPumpingContinuous','optical_pumping_continuous_duration'),
#                   ('OpticalPumpingContinuous','optical_pumping_continuous_repump_additional'),
#                   ('OpticalPumpingContinuous','optical_pumping_continuous_frequency_854'),
#                   ('OpticalPumpingContinuous','optical_pumping_continuous_amplitude_854'),
#                   ('OpticalPumpingContinuous','optical_pumping_continuous_frequency_729'),
#                   ('OpticalPumpingContinuous','optical_pumping_continuous_amplitude_729'),
#                   ('OpticalPumpingContinuous','optical_pumping_continuous_frequency_866'), 
#                   ('OpticalPumpingContinuous','optical_pumping_continuous_amplitude_866'),
#             
#                   ]
# 
#     def sequence(self):
#         opc = self.parameters.OpticalPumpingContinuous
#         repump_dur_854 = opc.optical_pumping_continuous_duration + opc.optical_pumping_continuous_repump_additional
#         repump_dur_866 = opc.optical_pumping_continuous_duration + 2 * opc.optical_pumping_continuous_repump_additional
#         self.end = self.start + repump_dur_866
#         self.addDDS('729', self.start, opc.optical_pumping_continuous_duration, opc.optical_pumping_continuous_frequency_729, opc.optical_pumping_continuous_amplitude_729)
#         self.addDDS('854', self.start, repump_dur_854, opc.optical_pumping_continuous_frequency_854, opc.optical_pumping_continuous_amplitude_854)
#         self.addDDS('866', self.start, repump_dur_866, opc.optical_pumping_continuous_frequency_866, opc.optical_pumping_continuous_amplitude_866)