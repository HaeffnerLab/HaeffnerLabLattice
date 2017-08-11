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
        #this hack will be not needed with the new dds parsing methods
        p = self.parameters.Excitation_729
        # 729 params
        channel_729 = p.channel_729
        freq_729 = p.rabi_excitation_frequency
        amp_729  = p.rabi_excitation_amplitude
        duration_729 = p.rabi_excitation_duration
        phase_729 = p.rabi_excitation_phase
         
        #rf = self.parameters.RabiFlopping      
        frequency_advance_duration = WithUnit(6, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        
        #freq_729=self.calc_freq(rf.line_selection)
        self.end = self.start + frequency_advance_duration + duration_729
    
        #first advance the frequency but keep amplitude low        
        self.addDDS(p.channel_729, self.start, frequency_advance_duration, freq_729, ampl_off)
        
        #turn on
        print "RABI EXCITATION"
        print "729 channel:.{}".format(channel_729)
        print "729 duration:.{}".format(duration_729)
        print "729 amp:.{}".format(amp_729)
        print "729 freq:.{}".format(freq_729)
        
        
        self.addDDS(channel_729, self.start + frequency_advance_duration, duration_729, freq_729, amp_729, phase_729)
        
        # adding the bichro beam 
        if p.bichro:
            pl = self.parameters.LocalStarkShift
            f = WithUnit(80. - 0.2, 'MHz') + pl.detuning
            # only one of these double passes should be on so it shouldn't hurt to do both TTLs
            self.addTTL('bichromatic_1', self.start, + duration_729 + frequency_advance_duration)
            self.addTTL('bichromatic_2', self.start, + duration_729 + frequency_advance_duration)
           # self.addDDS('SP_local', self.start + frequency_advance_duration, duration_729, f, pl.amplitude)
            self.end = self.end + WithUnit(2.0, 'us') # small buffer to turn off the TTL

            
            
            
