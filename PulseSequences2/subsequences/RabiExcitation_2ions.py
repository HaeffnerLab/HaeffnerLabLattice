from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

  
class RabiExcitation_2ions(pulse_sequence):
    '''
    Runs a 729 excitation with the Excitation_729 params
    channel_729
    
    rabi_excitation_amp
    rabi_excitation_duration
    rabi_excitation_frequency
    rabi_excitation_phase
    '''
    

    def sequence(self):
        
        ampl_off = WithUnit(-63.0, 'dBm')
        frequency_advance_duration = WithUnit(6, 'us')
        
        p= self.parameters.RabiFlopping_2ions

        freq_729_global_2 = self.calc_freq(p.ion1_line_selection)
        amp_729_global_2 =  p.ion1_rabi_amplitude_729

        freq_729_global_3 = self.calc_freq(p.ion0_line_selection)
        amp_729_global_3 =  p.ion0_rabi_amplitude_729

        duration_729 = p.duration
        
#       print "Rabi Excitation sub sequence"
#       print "729 freq: {}".format(freq_729.inUnitsOf('MHz'))
#        print "729 amp is {}".format(amp_729)
#        print "729 duration is {}".format(duration_729)
         
        #first advance the frequency but keep amplitude low        
        self.addDDS('729global_2', self.start, frequency_advance_duration, freq_729_global_2, ampl_off)
        self.addDDS('729global_3', self.start, frequency_advance_duration, freq_729_global_3, ampl_off)

        self.addDDS('729global_2', self.start + frequency_advance_duration, duration_729, freq_729_global_2, amp_729_global_2)
        self.addDDS('729global_3', self.start + frequency_advance_duration, duration_729, freq_729_global_3, amp_729_global_3)
        
        
        self.end = self.start + frequency_advance_duration + duration_729
                    
        # adding the bichro beam 
        #if p.bichro:
        #    pl = self.parameters.LocalStarkShift
        #    f = WithUnit(80. - 0.2, 'MHz') + pl.detuning
        #    # only one of these double passes should be on so it shouldn't hurt to do both TTLs
        #    self.addTTL('bichromatic_1', self.start, + duration_729 + frequency_advance_duration)
        #    self.addTTL('bichromatic_2', self.start, + duration_729 + frequency_advance_duration)
           # self.addDDS('SP_local', self.start + frequency_advance_duration, duration_729, f, pl.amplitude)
        #    self.end = self.end + WithUnit(2.0, 'us') # small buffer to turn off the TTL

            
            
            
