from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from lattice.scripts.PulseSequences.subsequences.DopplerCooling import doppler_cooling
from EmptySequence import empty_sequence
from treedict import TreeDict

class global_blue_heating(pulse_sequence):
    
    required_parameters = [
                            ('Heating','global_blue_heating_frequency_397'), 
                            ('Heating','global_blue_heating_amplitude_397'), 
                            ('Heating','blue_heating_frequency_866'), 
                            ('Heating','blue_heating_amplitude_866'), 
                            ('Heating','blue_heating_duration'),
                            ('Heating','blue_heating_repump_additional')
                            ]
    
    required_subsequences = [doppler_cooling]
    
    def sequence(self):
        h = self.parameters.Heating
        replace = {
                   'DopplerCooling.doppler_cooling_frequency_397':h.global_blue_heating_frequency_397,
                   'DopplerCooling.doppler_cooling_amplitude_397':h.global_blue_heating_amplitude_397,
                   'DopplerCooling.doppler_cooling_frequency_866':h.blue_heating_frequency_866,
                   'DopplerCooling.doppler_cooling_amplitude_866':h.blue_heating_amplitude_866,
                   'DopplerCooling.doppler_cooling_duration':h.blue_heating_duration,
                   'DopplerCooling.doppler_cooling_repump_additional':h.blue_heating_repump_additional
                   }
        self.addSequence(doppler_cooling, TreeDict.fromdict(replace))

class local_blue_heating(pulse_sequence):
    
    required_parameters = [
                            ('Heating','local_blue_heating_frequency_397'), 
                            ('Heating','local_blue_heating_amplitude_397'), 
                            ('Heating','blue_heating_frequency_866'), 
                            ('Heating','blue_heating_amplitude_866'), 
                            ('Heating','blue_heating_duration'),
                            ('Heating','blue_heating_repump_additional')
                          ]
    
    required_subsequences = [doppler_cooling]
    
    def sequence(self):
        h = self.parameters.Heating
        repump_duration = h.blue_heating_duration + h.blue_heating_repump_additional
        self.addDDS('radial',self.start, h.blue_heating_duration, h.local_blue_heating_frequency_397, h.local_blue_heating_amplitude_397)
        if h.blue_heating_duration['s'] > 40e-9:
            self.addTTL ('radial', self.start, h.blue_heating_duration)
        self.addDDS ('866',self.start, repump_duration, h.blue_heating_frequency_866, h.blue_heating_amplitude_866)
        self.end = self.start + repump_duration
        
class blue_heating(pulse_sequence):
    
    required_parameters = [
                        ('Heating','blue_heating_type'), 
                        ('Heating','blue_heating_delay_before'), 
                        ('Heating','blue_heating_delay_after'), 
                      ]
    
    
    required_subsequences = [global_blue_heating, local_blue_heating, empty_sequence]
    
    def sequence(self):
        h = self.parameters.Heating
        self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':h.blue_heating_delay_before}))
        if h.blue_heating_type == 'global':
            self.addSequence(global_blue_heating)
        elif h.blue_heating_type =='local':
            self.addSequence(local_blue_heating)
        else:
            raise Exception("Incorrect Heating Type")
        self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':h.blue_heating_delay_after}))