from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit
from DopplerCooling import doppler_cooling

class ramsey_2ions_excitation(pulse_sequence):
    
    required_parameters = [
                          ('Ramsey_2ions','ion1_excitation_frequency1'),
                          ('Ramsey_2ions','ion1_excitation_amplitude1'),
                          ('Ramsey_2ions','ion1_excitation_duration1'),
                          ('Ramsey_2ions','ion1_excitation_frequency2'),
                          ('Ramsey_2ions','ion1_excitation_amplitude2'),
                          ('Ramsey_2ions','ion1_excitation_duration2'),
                          ('Ramsey_2ions','ion2_excitation_frequency1'),
                          ('Ramsey_2ions','ion2_excitation_amplitude1'),
                          ('Ramsey_2ions','ion2_excitation_duration1'),
                          ('Ramsey_2ions','ion2_excitation_frequency2'),
                          ('Ramsey_2ions','ion2_excitation_amplitude2'),
                          ('Ramsey_2ions','ion2_excitation_duration2'),
                          ('Ramsey_2ions','ramsey_time'),
                          ]
    required_subsequences = [doppler_cooling]

    def sequence(self):
        #this hack will be not needed with the new dds parsing methods
        p = self.parameters.Ramsey_2ions
        frequency_advance_duration = WithUnit(6, 'us')
        gap = WithUnit(2, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        
        #self.end = self.start + frequency_advance_duration + p.rabi_excitation_duration
        self.end = self.start
        ###set all frequencies but keep amplitude low first###
        self.addDDS('729', self.end, frequency_advance_duration, p.ion1_excitation_frequency1, ampl_off)
        self.addDDS('729_1', self.end, frequency_advance_duration, p.ion1_excitation_frequency2, ampl_off)        
        self.addDDS('729_aux', self.end, frequency_advance_duration, p.ion2_excitation_frequency1, ampl_off)
        self.addDDS('729_aux_1', self.end, frequency_advance_duration, p.ion2_excitation_frequency2, ampl_off)
        self.end = self.end + frequency_advance_duration
        
        ###first rabi excitation on ion1###
        self.addDDS('729', self.end, p.ion1_excitation_duration1, p.ion1_excitation_frequency1, p.ion1_excitation_amplitude1)
        self.end = self.end + p.ion1_excitation_duration1 + gap
        
        ###second rabi excitation on ion1###                
        self.addDDS('729_1', self.end, p.ion1_excitation_duration2, p.ion1_excitation_frequency2, p.ion1_excitation_amplitude2)
        self.end = self.end + p.ion1_excitation_duration2 + gap       
        
        ###first rabi excitation on ion2###
        self.addDDS('729_aux', self.end, p.ion2_excitation_duration1, p.ion2_excitation_frequency1, p.ion2_excitation_amplitude1)
        self.end = self.end + p.ion2_excitation_duration1 + gap   
        
        ###second rabi excitation on ion2###                
        self.addDDS('729_aux_1', self.end, p.ion2_excitation_duration2, p.ion2_excitation_frequency2, p.ion2_excitation_amplitude2)
        self.end = self.end + p.ion2_excitation_duration2 + gap
        
        ###add ramsey time which we do nothing###
        self.end = self.end+p.ramsey_time
        
        ### add doppler cooling
        #self.addSequence(doppler_cooling)
        
        ###undoing stuff###
        ###second rabi excitation on ion2###                
        self.addDDS('729_aux_1', self.end, p.ion2_excitation_duration2, p.ion2_excitation_frequency2, p.ion2_excitation_amplitude2)
        self.end = self.end + p.ion2_excitation_duration2 + gap
        ###first rabi excitation on ion2###
        self.addDDS('729_aux', self.end, p.ion2_excitation_duration1, p.ion2_excitation_frequency1, p.ion2_excitation_amplitude1)
        self.end = self.end + p.ion2_excitation_duration1 + gap
        ###second rabi excitation on ion1###                
        self.addDDS('729_1', self.end, p.ion1_excitation_duration2, p.ion1_excitation_frequency2, p.ion1_excitation_amplitude2)
        self.end = self.end + p.ion1_excitation_duration2 + gap    
        ###first rabi excitation on ion1###
        self.addDDS('729', self.end, p.ion1_excitation_duration1, p.ion1_excitation_frequency1, p.ion1_excitation_amplitude1)
        self.end = self.end + p.ion1_excitation_duration1 + gap

