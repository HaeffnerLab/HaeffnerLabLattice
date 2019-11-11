from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class OpticalPumping(pulse_sequence):
    
    '''
    Optical pumping unig a frequency selective transition  
    '''


    def sequence(self):
        op = self.parameters.OpticalPumping
        opc = self.parameters.OpticalPumpingContinuous
         
         
        channel_729 = self.parameters.StatePreparation.channel_729
        # choose the carrier frequency
        freq_729 = self.calc_freq(op.line_selection)
        #print "Optical pumping 729 freq:.{}".format(freq_729)        
        #print "Optical pumping line selection:.{}".format(op.line_selection)
        #print channel_729
        repump_dur_854 = opc.optical_pumping_continuous_duration + opc.optical_pumping_continuous_repump_additional
        repump_dur_866 = opc.optical_pumping_continuous_duration + 2 * opc.optical_pumping_continuous_repump_additional
        self.end = self.start + repump_dur_866
        
        self.addDDS(channel_729, self.start, opc.optical_pumping_continuous_duration, freq_729, op.optical_pumping_amplitude_729)
        #print 'op:', opc.optical_pumping_continuous_frequency_729
        #print 'op:',  opc.optical_pumping_continuous_duration
        self.addDDS('854', self.start, repump_dur_854, op.optical_pumping_frequency_854, op.optical_pumping_amplitude_854)
        #self.addDDS('866', self.start, repump_dur_866, op.optical_pumping_frequency_866, op.optical_pumping_amplitude_866)
        # changing the 866 from a dds to a rf source enabled by a switch
        self.addTTL('866DP', self.start + WithUnit(0.25, 'us'), repump_dur_866 - WithUnit(0.1, 'us') )
        #aux = self.parameters.OpticalPumpingAux
        #if aux.aux_op_enable:
            #self.addDDS('729DP_aux', self.start, opc.optical_pumping_continuous_duration, aux.aux_optical_frequency_729, aux.aux_optical_pumping_amplitude_729)
            #print 'aux op:', aux.aux_optical_frequency_729
