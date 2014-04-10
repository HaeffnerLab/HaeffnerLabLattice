from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class rabi_excitation_2ions(pulse_sequence):
    
    required_parameters = [
                          ('Rabi_excitation_729_2ions','ion1_excitation_frequency'),
                          ('Rabi_excitation_729_2ions','ion1_excitation_amplitude'),
                          ('Rabi_excitation_729_2ions','ion1_excitation_duration'),
                          ('Rabi_excitation_729_2ions','ion1_excitation_phase'),
                          ('Rabi_excitation_729_2ions','ion2_excitation_frequency'),
                          ('Rabi_excitation_729_2ions','ion2_excitation_amplitude'),
                          ('Rabi_excitation_729_2ions','ion2_excitation_duration'),
                          ('Rabi_excitation_729_2ions','ion2_excitation_phase'),
                          ('Rabi_excitation_729_2ions','use_primary_dds'),
                          ]

    def sequence(self):
        #this hack will be not needed with the new dds parsing methods
        p = self.parameters.Rabi_excitation_729_2ions
        frequency_advance_duration = WithUnit(6, 'us')
        gap = WithUnit(2, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        self.end = self.start
        #first advance the frequency but keep amplitude low      
        if p.use_primary_dds:  
            print 'use_primary_dds'
            self.addDDS('729', self.end, frequency_advance_duration, p.ion1_excitation_frequency, ampl_off)
            self.addDDS('729_aux', self.end, frequency_advance_duration, p.ion2_excitation_frequency, ampl_off)
            self.end = self.end+frequency_advance_duration
        ## add first excitation pulse
            self.addDDS('729', self.end, p.ion1_excitation_duration, p.ion1_excitation_frequency, p.ion1_excitation_amplitude,p.ion1_excitation_phase)
            self.end = self.end+p.ion1_excitation_duration+gap
            #print 'ion1 power is', p.ion1_excitation_amplitude
        #turn on
            self.addDDS('729_aux', self.end, p.ion2_excitation_duration, p.ion2_excitation_frequency, p.ion2_excitation_amplitude,p.ion2_excitation_phase)
            self.end = self.end+p.ion2_excitation_duration+gap
            #print 'ion2 power is', p.ion2_excitation_amplitude
        else:
            print 'use_secondary_dds'
            self.addDDS('729_1', self.end, frequency_advance_duration, p.ion1_excitation_frequency, ampl_off)
            self.addDDS('729_aux_1', self.end, frequency_advance_duration, p.ion2_excitation_frequency, ampl_off)
            self.end = self.end+frequency_advance_duration

        ## add first excitation pulse
            self.addDDS('729_1', self.end, p.ion1_excitation_duration, p.ion1_excitation_frequency, p.ion1_excitation_amplitude,p.ion1_excitation_phase)
            self.end = self.end+p.ion1_excitation_duration+gap
            #print 'ion1 power is', p.ion1_excitation_amplitude
#         self.addDDS('729DP_aux', self.start, frequency_advance_duration, p.rabi_excitation_frequency, ampl_off)
        #turn on
            self.addDDS('729_aux_1', self.end, p.ion2_excitation_duration, p.ion2_excitation_frequency, p.ion2_excitation_amplitude,p.ion2_excitation_phase)
            self.end = self.end+p.ion2_excitation_duration+gap
            #print 'ion2 power is', p.ion2_excitation_amplitude
