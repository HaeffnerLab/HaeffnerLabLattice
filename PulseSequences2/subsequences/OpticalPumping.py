from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence

class optical_pumping(pulse_sequence):
    
    


    def sequence(self):
        opc = self.parameters.OpticalPumpingContinuous
        channel_729 = self.parameters.StatePreparation.channel_729
        #print channel_729
        repump_dur_854 = opc.optical_pumping_continuous_duration + opc.optical_pumping_continuous_repump_additional
        repump_dur_866 = opc.optical_pumping_continuous_duration + 2 * opc.optical_pumping_continuous_repump_additional
        self.end = self.start + repump_dur_866
        self.addDDS(channel_729, self.start, opc.optical_pumping_continuous_duration, opc.optical_pumping_continuous_frequency_729, opc.optical_pumping_continuous_amplitude_729)
        #print 'op:', opc.optical_pumping_continuous_frequency_729
        #print 'op:',  opc.optical_pumping_continuous_duration
        self.addDDS('854', self.start, repump_dur_854, opc.optical_pumping_continuous_frequency_854, opc.optical_pumping_continuous_amplitude_854)
        self.addDDS('866', self.start, repump_dur_866, opc.optical_pumping_continuous_frequency_866, opc.optical_pumping_continuous_amplitude_866)
        aux = self.parameters.OpticalPumpingAux
        if aux.aux_op_enable:
            self.addDDS('729DP_aux', self.start, opc.optical_pumping_continuous_duration, aux.aux_optical_frequency_729, aux.aux_optical_pumping_amplitude_729)
            print 'aux op:', aux.aux_optical_frequency_729
