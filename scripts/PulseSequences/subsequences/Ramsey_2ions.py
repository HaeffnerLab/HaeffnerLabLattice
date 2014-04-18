from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit
from DopplerCooling import doppler_cooling
from treedict import TreeDict

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
                          ('Ramsey_2ions','ion2_excitation_phase1'),
                          ('Ramsey_2ions','ramsey_time'),
                          ('Ramsey2ions_ScanGapParity', 'sympathetic_cooling_enable'),
                          ('DopplerCooling','doppler_cooling_repump_additional')
                          ]
    required_subsequences = [doppler_cooling]
    replaced_parameters = {doppler_cooling:[('DopplerCooling','doppler_cooling_duration')]
                           }

    def sequence(self):
        #this hack will be not needed with the new dds parsing methods
        p = self.parameters.Ramsey_2ions
        frequency_advance_duration = WithUnit(8.0, 'us')
        gap = WithUnit(1.0, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        
        #detuning = WithUnit(0.0,'kHz')
        
        #self.end = self.start + frequency_advance_duration + p.rabi_excitation_duration
        self.end = self.start
        #print self.end
        ###set all frequencies but keep amplitude low first###
        self.addDDS('729', self.end, frequency_advance_duration, p.ion1_excitation_frequency1, ampl_off)
        self.addDDS('729_1', self.end, frequency_advance_duration, p.ion1_excitation_frequency2, ampl_off)        
        self.addDDS('729_aux', self.end, frequency_advance_duration, p.ion2_excitation_frequency1, ampl_off)
        self.addDDS('729_aux_1', self.end, frequency_advance_duration, p.ion2_excitation_frequency2, ampl_off)
        self.end = self.end + frequency_advance_duration
        
        ###pi/2 pulses###
        self.addDDS('729', self.end, p.ion1_excitation_duration1, p.ion1_excitation_frequency1, p.ion1_excitation_amplitude1)
        self.addDDS('729_aux', self.end, p.ion2_excitation_duration1, p.ion2_excitation_frequency1, p.ion2_excitation_amplitude1)
        print 'left ion pulse 1:', p.ion1_excitation_duration1, p.ion1_excitation_frequency1, p.ion1_excitation_amplitude1
        print 'right ion pulse 1:', p.ion2_excitation_duration1, p.ion2_excitation_frequency1, p.ion2_excitation_amplitude1
        self.end = self.end + max(p.ion1_excitation_duration1,p.ion2_excitation_duration1) + gap
        
        ###pi pulses###
        
        self.addDDS('729_1', self.end, p.ion1_excitation_duration2, p.ion1_excitation_frequency2, p.ion1_excitation_amplitude2)
        self.addDDS('729_aux_1', self.end, p.ion2_excitation_duration2, p.ion2_excitation_frequency2, p.ion2_excitation_amplitude2)
        print 'left ion pulse 2:', p.ion1_excitation_duration2, p.ion1_excitation_frequency2, p.ion1_excitation_amplitude2
        print 'right ion pulse 2:', p.ion2_excitation_duration2, p.ion2_excitation_frequency2, p.ion2_excitation_amplitude2
        self.end = self.end + max(p.ion1_excitation_duration2,p.ion2_excitation_duration2) + gap   
        
        ### ramsey time ###
        
        
        
        self.end = self.end+p.ramsey_time - WithUnit(20.0,'us')
        
        self.addDDS('global397', self.end, WithUnit(20.0,'us'), WithUnit(90.0,'MHz'), WithUnit(-12.0,'dBm'))
         
        self.end = self.end + WithUnit(20.0,'us')
        
        print 'Ramsey_time:', p.ramsey_time
        
        ### undo pi pulses
         
        self.addDDS('729_1', self.end, p.ion1_excitation_duration2, p.ion1_excitation_frequency2, p.ion1_excitation_amplitude2,WithUnit(180,'deg'))
        self.addDDS('729_aux_1', self.end, p.ion2_excitation_duration2, p.ion2_excitation_frequency2, p.ion2_excitation_amplitude2,WithUnit(180,'deg'))
        #print 'left ion pulse 2:', p.ion1_excitation_duration2, p.ion1_excitation_frequency2, p.ion1_excitation_amplitude2
        self.end = self.end + max(p.ion1_excitation_duration2,p.ion2_excitation_duration2) + gap  
        
        ###pi/2 pulses###
        self.addDDS('729', self.end, p.ion1_excitation_duration1, p.ion1_excitation_frequency1, p.ion1_excitation_amplitude1,WithUnit(180,'deg'))
        self.addDDS('729_aux', self.end, p.ion2_excitation_duration1, p.ion2_excitation_frequency1, p.ion2_excitation_amplitude1,p.ion2_excitation_phase1)
        print 'phase:', p.ion2_excitation_phase1
        self.end = self.end + max(p.ion1_excitation_duration1,p.ion2_excitation_duration1) + gap