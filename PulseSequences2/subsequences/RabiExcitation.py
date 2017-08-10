from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

  
class RabiExcitation(pulse_sequence):
    '''
    729 Rabi Excitation select channel
    729 excitation 
    729- channel, freq, amp, ac stark shift
    '''
    

    def sequence(self):
        #this hack will be not needed with the new dds parsing methods
        p = self.parameters.Excitation_729
        rf = self.parameters.RabiFlopping      
        frequency_advance_duration = WithUnit(6, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        
        freq_729=self.calc_freq(rf.line_selection)
        self.end = self.start + frequency_advance_duration + p.rabi_excitation_duration
    
        #first advance the frequency but keep amplitude low        
        self.addDDS(p.channel_729, self.start, frequency_advance_duration, freq_729, ampl_off)
        
        #turn on
        print "RABI EXCITATION DURATION"
        print p.rabi_excitation_duration
        self.addDDS(p.channel_729, self.start + frequency_advance_duration, p.rabi_excitation_duration, freq_729, p.rabi_excitation_amplitude, p.rabi_excitation_phase)
        
        #print p.rabi_excitation_amplitude
        if p.bichro:
            pl = self.parameters.LocalStarkShift
            f = WithUnit(80. - 0.2, 'MHz') + pl.detuning
            # only one of these double passes should be on so it shouldn't hurt to do both TTLs
            self.addTTL('bichromatic_1', self.start, + p.rabi_excitation_duration + frequency_advance_duration)
            self.addTTL('bichromatic_2', self.start, + p.rabi_excitation_duration + frequency_advance_duration)
            self.addDDS('SP_local', self.start + frequency_advance_duration, p.rabi_excitation_duration, f, pl.amplitude)
            self.end = self.end + WithUnit(2.0, 'us') # small buffer to turn off the TTL

            
            
            
