from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class rabi_excitation(pulse_sequence):
    
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
        self.addDDS('729', self.start, frequency_advance_duration, p.rabi_excitation_frequency, ampl_off)
#         self.addDDS('729DP_aux', self.start, frequency_advance_duration, p.rabi_excitation_frequency, ampl_off)
        #turn on
        self.addDDS('729', self.start + frequency_advance_duration, p.rabi_excitation_duration, p.rabi_excitation_frequency, p.rabi_excitation_amplitude, p.rabi_excitation_phase)
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
                          ]
    
    def sequence(self):
        p = self.parameters.Excitation_729
        self.end = self.start + p.rabi_excitation_duration
        self.addDDS('729', self.start, p.rabi_excitation_duration, p.rabi_excitation_frequency, p.rabi_excitation_amplitude, p.rabi_excitation_phase)
    
class rabi_excitation_select_channel(pulse_sequence):
    
    required_parameters = [
                            ('Excitation_729','channel_729'),
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
        self.addDDS(p.channel_729, self.start, frequency_advance_duration, p.rabi_excitation_frequency, ampl_off)
        #turn on
        self.addDDS(p.channel_729, self.start + frequency_advance_duration, p.rabi_excitation_duration, p.rabi_excitation_frequency, p.rabi_excitation_amplitude, p.rabi_excitation_phase)