from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class rabi_excitation(pulse_sequence):
    
    required_parameters = [
                          ('Excitation_729','rabi_excitation_frequency'),
                          ('Excitation_729','rabi_excitation_amplitude'),
                          ('Excitation_729','rabi_excitation_duration'),
                          ('Excitation_729','rabi_excitation_phase'),
                          ('Excitation_729', 'channel_729'),
                          ]

    def sequence(self):
        #this hack will be not needed with the new dds parsing methods
        p = self.parameters.Excitation_729
        frequency_advance_duration = WithUnit(6, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        self.end = self.start + frequency_advance_duration + p.rabi_excitation_duration
        print p.channel_729

        #first advance the frequency but keep amplitude low        
        self.addDDS(p.channel_729, self.start, frequency_advance_duration, p.rabi_excitation_frequency, ampl_off)
#         self.addDDS('729DP_aux', self.start, frequency_advance_duration, p.rabi_excitation_frequency, ampl_off)
        #turn on
        self.addDDS(p.channel_729, self.start + frequency_advance_duration, p.rabi_excitation_duration, p.rabi_excitation_frequency, p.rabi_excitation_amplitude, p.rabi_excitation_phase)
#         self.addDDS('729DP_aux', self.start + frequency_advance_duration, p.rabi_excitation_duration, p.rabi_excitation_frequency, p.rabi_excitation_amplitude, p.rabi_excitation_phase)

class rabi_excitation_second_dds(pulse_sequence):
    
    required_parameters = [
                          ('Excitation_729','rabi_excitation_frequency'),
                          ('Excitation_729','rabi_excitation_amplitude'),
                          ('Excitation_729','rabi_excitation_duration'),
                          ('Excitation_729','rabi_excitation_phase'),
                          ]

    def sequence(self):
        #this hack will be not needed with the new dds parsing methods
        p = self.parameters.Excitation_729
        frequency_advance_duration = WithUnit(6, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        self.end = self.start + frequency_advance_duration + p.rabi_excitation_duration
        #first advance the frequency but keep amplitude low        
        self.addDDS('729_1', self.start, frequency_advance_duration, p.rabi_excitation_frequency, ampl_off)
        #turn on
        self.addDDS('729_1', self.start + frequency_advance_duration, p.rabi_excitation_duration, p.rabi_excitation_frequency, p.rabi_excitation_amplitude, p.rabi_excitation_phase)
        
class rabi_excitation_no_offset(pulse_sequence):
    
    required_parameters = [
                          ('Excitation_729','rabi_excitation_frequency'),
                          ('Excitation_729','rabi_excitation_amplitude'),
                          ('Excitation_729','rabi_excitation_duration'),
                          ('Excitation_729','rabi_excitation_phase'),
                          ('Excitation_729', 'channel_729'),
                          ]
    
    def sequence(self):
        p = self.parameters.Excitation_729
        self.end = self.start + p.rabi_excitation_duration
        self.addDDS(p.channel_729, self.start, p.rabi_excitation_duration, p.rabi_excitation_frequency, p.rabi_excitation_amplitude, p.rabi_excitation_phase)
    
class rabi_excitation_select_channel(pulse_sequence):
    
    required_parameters = [
                            ('Excitation_729','channel_729'),
                            ('Excitation_729','bichro'),
                            ('Excitation_729','rabi_excitation_frequency'),
                            ('Excitation_729','rabi_excitation_amplitude'),
                            ('Excitation_729','rabi_excitation_duration'),
                            ('Excitation_729','rabi_excitation_phase'),
                            
                          ('LocalStarkShift', 'enable'),
                          ('LocalStarkShift','amplitude'),
                          ('LocalStarkShift', 'detuning'), # detuning from the carrier transition
                          ]

    def sequence(self):
        #this hack will be not needed with the new dds parsing methods
        p = self.parameters.Excitation_729
        #q = self.parameters.LocalStarkShift
        frequency_advance_duration = WithUnit(6, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        #f0 = WithUnit(80., 'MHz') # base frequency for Stark shift laser
        self.end = self.start + frequency_advance_duration + p.rabi_excitation_duration
        #first advance the frequency but keep amplitude low        
        self.addDDS(p.channel_729, self.start, frequency_advance_duration, p.rabi_excitation_frequency, ampl_off)
        #if q.enable: # also turn on local stark shift
        #    self.addDDS('stark_shift', self.start, frequency_advance_duration, f0 + q.detuning, ampl_off)
        #    self.addDDS('729DP_1', self.start, frequency_advance_duration, p.rabi_excitation_frequency, ampl_off)
        #turn on
        self.addDDS(p.channel_729, self.start + frequency_advance_duration, p.rabi_excitation_duration, p.rabi_excitation_frequency, p.rabi_excitation_amplitude, p.rabi_excitation_phase)
        #self.addDDS('SP_local', self.start + frequency_advance_duration, p.rabi_excitation_duration, WithUnit(80., 'MHz'), WithUnit(-12., 'dBm')  )
        #if q.enable:
        #    self.addDDS('stark_shift', self.start + frequency_advance_duration, p.rabi_excitation_duration, f0 + q.detuning, q.amplitude)
        #    self.addDDS('729DP_1', self.start + frequency_advance_duration, p.rabi_excitation_duration, p.rabi_excitation_frequency, WithUnit(-12, 'dBm'))
        #    self.addTTL('bichromatic_2', self.start, + p.rabi_excitation_duration + frequency_advance_duration) # REMOVE THIS LATER
        print p.rabi_excitation_amplitude
        if p.bichro:
            pl = self.parameters.LocalStarkShift
            f = WithUnit(80. - 0.2, 'MHz') + pl.detuning
            # only one of these double passes should be on so it shouldn't hurt to do both TTLs
            self.addTTL('bichromatic_1', self.start, + p.rabi_excitation_duration + frequency_advance_duration)
            self.addTTL('bichromatic_2', self.start, + p.rabi_excitation_duration + frequency_advance_duration)
            self.addDDS('SP_local', self.start + frequency_advance_duration, p.rabi_excitation_duration, f, pl.amplitude)
            self.end = self.end + WithUnit(2.0, 'us') # small buffer to turn off the TTL

            
            
            
