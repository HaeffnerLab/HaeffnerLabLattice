from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class OpticalPumpingPulsed(pulse_sequence):
    
    '''
    Optical pumping unig a frequency selective transition  
    '''


    def sequence(self):
        op = self.parameters.OpticalPumping
        opc = self.parameters.OpticalPumpingContinuous
        sp = self.parameters.StatePreparation
         
         
        channel_729 = self.parameters.StatePreparation.channel_729
        # choose the carrier frequency
        freq_729 = self.calc_freq(op.line_selection)
        #print "Optical pumping 729 freq:.{}".format(freq_729)        
        #print "Optical pumping line selection:.{}".format(op.line_selection)
        #print channel_729
        repump_dur_854 = sp.pulsed_854_duration
        repump_dur_866 = (sp.pi_time + 3 * repump_dur_854) * 2
        self.end = self.start + repump_dur_866
        
        self.addDDS(channel_729, self.start, sp.pi_time, freq_729, sp.pulsed_amplitude)
        #print 'op:', opc.optical_pumping_continuous_frequency_729
        #print 'op:',  opc.optical_pumping_continuous_duration
        self.addDDS('854', self.start + sp.pi_time, repump_dur_854, op.optical_pumping_frequency_854, op.optical_pumping_amplitude_854)
        #self.addDDS('866', self.start, repump_dur_866, op.optical_pumping_frequency_866, op.optical_pumping_amplitude_866)
        # changing the 866 from a dds to a rf source enabled by a switch
        self.addTTL('866DP', self.start + WithUnit(0.25, 'us'), repump_dur_866 - WithUnit(0.1, 'us') )
        #aux = self.parameters.OpticalPumpingAux
        #if aux.aux_op_enable:
            #self.addDDS('729DP_aux', self.start, opc.optical_pumping_continuous_duration, aux.aux_optical_frequency_729, aux.aux_optical_pumping_amplitude_729)
            #print 'aux op:', aux.aux_optical_frequency_729
