from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from lattice.scripts.PulseSequences.subsequences.DopplerCooling import doppler_cooling
from EmptySequence import empty_sequence
from treedict import TreeDict
from labrad.units import WithUnit

# class global_blue_heating(pulse_sequence):
#     
#     required_parameters = [
#                             ('Heating','global_blue_heating_frequency_397'), 
#                             ('Heating','global_blue_heating_amplitude_397'), 
#                             ('Heating','blue_heating_frequency_866'), 
#                             ('Heating','blue_heating_amplitude_866'), 
#                             ('Heating','blue_heating_duration'),
#                             ('Heating','blue_heating_repump_additional')
#                             ]
#     
#     required_subsequences = [doppler_cooling]
#     
#     def sequence(self):
#         h = self.parameters.Heating
#         replace = {
#                    'DopplerCooling.doppler_cooling_frequency_397':h.global_blue_heating_frequency_397,
#                    'DopplerCooling.doppler_cooling_amplitude_397':h.global_blue_heating_amplitude_397,
#                    'DopplerCooling.doppler_cooling_frequency_866':h.blue_heating_frequency_866,
#                    'DopplerCooling.doppler_cooling_amplitude_866':h.blue_heating_amplitude_866,
#                    'DopplerCooling.doppler_cooling_duration':h.blue_heating_duration,
#                    'DopplerCooling.doppler_cooling_repump_additional':h.blue_heating_repump_additional
#                    }
#         self.addSequence(doppler_cooling, TreeDict.fromdict(replace))

class local_blue_heating(pulse_sequence):
    
    required_parameters = [
                            ('Heating','local_blue_heating_frequency_397'), 
                            ('Heating','local_blue_heating_amplitude_397'), 
                            ('Heating','blue_heating_frequency_866'), 
                            ('Heating','blue_heating_amplitude_866'), 
                            ('Heating','blue_heating_duration'),
                            ('Heating','blue_heating_repump_additional')
                          ]
    
    def sequence(self):
        h = self.parameters.Heating
        frequency_advance_duration = WithUnit(6, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        #make sure light turns on immediately with no delay
        repump_duration = frequency_advance_duration + h.blue_heating_duration + h.blue_heating_repump_additional
        self.addDDS('radial',self.start, frequency_advance_duration, h.local_blue_heating_frequency_397, ampl_off)
        self.addDDS('radial',self.start + frequency_advance_duration, h.blue_heating_duration, h.local_blue_heating_frequency_397, h.local_blue_heating_amplitude_397)
        self.addDDS ('866',self.start, repump_duration, h.blue_heating_frequency_866, h.blue_heating_amplitude_866)
        self.end = self.start + repump_duration

class blue_heating(pulse_sequence):
    
    required_parameters = [
                        ('Heating','blue_heating_delay_before'), 
                        ('Heating','blue_heating_delay_after'), 
                      ]
    
    required_subsequences = [local_blue_heating, empty_sequence]
    replaced_parameters = {empty_sequence:[('EmptySequence','empty_sequence_duration')]
                          }
    
    def sequence(self):
        h = self.parameters.Heating
        self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':h.blue_heating_delay_before}))
        self.addSequence(local_blue_heating)
        self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':h.blue_heating_delay_after}))