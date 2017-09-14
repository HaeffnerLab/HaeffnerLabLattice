from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

  
class RabiExcitation(pulse_sequence):
    '''
    Runs a 729 excitation with the Excitation_729 params
    channel_729
    
    rabi_excitation_amp
    rabi_excitation_duration
    rabi_excitation_frequency
    rabi_excitation_phase
    '''
    

    def sequence(self):
        
        #rf = self.parameters.RabiFlopping
        
        #if rf.selection_sideband == "off":         
        #    freq_729=self.calc_freq(rf.line_selection)
        #else:
        #    freq_729=self.calc_freq(rf.line_selection, rf.selection_sideband, int(rf.order))

        ampl_off = WithUnit(-63.0, 'dBm')
        frequency_advance_duration = WithUnit(6, 'us')
        
        freq_729 = self.parameters.Excitation_729.rabi_excitation_frequency
        duration_729 = self.parameters.Excitation_729.rabi_excitation_duration
        phase_729 = self.parameters.Excitation_729.rabi_excitation_phase
        amp_729 = self.parameters.Excitation_729.rabi_excitation_amplitude
        channel_729 = self.parameters.Excitation_729.channel_729
        #detuning = self.parameters.Excitation_729.detuning
        #freq_729 = freq_729 + detuning
        
#         
#         print "Rabi Excitation sub sequence"
#         print "729 freq: {}".format(freq_729.inUnitsOf('MHz'))
#         print "729 amp is {}".format(amp_729)
#         print "729 duration is {}".format(duration_729)
#         
        #first advance the frequency but keep amplitude low        
        self.addDDS(channel_729, self.start, frequency_advance_duration, freq_729, ampl_off)
        self.addDDS(channel_729, self.start + frequency_advance_duration, duration_729, freq_729, amp_729, phase_729)
        
        
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

            
            
            
