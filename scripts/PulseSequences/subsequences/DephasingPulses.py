from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from RabiExcitation import rabi_excitation, rabi_excitation_no_offset
from BlueHeating import blue_heating
from EmptySequence import empty_sequence
from labrad.units import WithUnit
from treedict import TreeDict

class dephasing_pulses(pulse_sequence):
    
    required_parameters = [
                           ('Dephasing_Pulses', 'preparation_pulse_frequency'),
                           ('Dephasing_Pulses', 'preparation_pulse_duration'),
                           ('Dephasing_Pulses', 'preparation_pulse_amplitude'),
                           
                           ('Dephasing_Pulses', 'evolution_pulses_frequency'),
                           ('Dephasing_Pulses', 'evolution_pulses_duration'),
                           ('Dephasing_Pulses', 'evolution_pulses_amplitude'),
                           ('Dephasing_Pulses', 'evolution_ramsey_time'),
                           ('Dephasing_Pulses', 'evolution_pulses_phase'),
                           
                           ('RamseyDephase','first_pulse_duration'),
                           ('RamseyDephase','pulse_gap'),
                           ('RamseyDephase','dephasing_frequency'),
                           ('RamseyDephase','dephasing_amplitude'),
                           ('RamseyDephase','dephasing_duration'),
                           ('RamseyDephase','second_pulse_duration'),
                           ('Heating','local_blue_heating_frequency_397'),
                           ('Heating','local_blue_heating_amplitude_397'),
                           ('Heating','blue_heating_frequency_866'),
                           ('Heating','blue_heating_amplitude_866'),
                           ('Heating','blue_heating_duration'),
                           ('Heating','blue_heating_repump_additional')
                           ]
    required_subsequences = [rabi_excitation, empty_sequence, rabi_excitation_no_offset, blue_heating]
    replaced_parameters = {empty_sequence:[('EmptySequence','empty_sequence_duration')],
                           rabi_excitation:[('Excitation_729','rabi_excitation_frequency'),
                                            ('Excitation_729','rabi_excitation_phase'),
                                            ('Excitation_729','rabi_excitation_amplitude'),
                                            ('Excitation_729','rabi_excitation_duration'),
                                            ],
                            rabi_excitation_no_offset:[('Excitation_729','rabi_excitation_frequency'),
                                            ('Excitation_729','rabi_excitation_phase'),
                                            ('Excitation_729','rabi_excitation_amplitude'),
                                            ('Excitation_729','rabi_excitation_duration'),
                                            ],
                           blue_heating:[ ('Excitation_729','rabi_excitation_frequency'),
                                            ('Excitation_729','rabi_excitation_phase'),
                                            ('Excitation_729','rabi_excitation_amplitude'),
                                            ('Excitation_729','rabi_excitation_duration'),
                                            ('Heating','local_blue_heating_frequency_397'),
                                            ('Heating','local_blue_heating_amplitude_397'),
                                            ('Heating','blue_heating_frequency_866'),
                                            ('Heating','blue_heating_amplitude_866'),
                                            ('Heating','blue_heating_duration'),
                                            ('Heating','blue_heating_repump_additional')]
                           }
                             
    def sequence(self):        
        p = self.parameters.Dephasing_Pulses
        replace_preparation = TreeDict.fromdict({
        'Excitation_729.rabi_excitation_frequency':p.preparation_pulse_frequency,
        'Excitation_729.rabi_excitation_duration':p.preparation_pulse_duration,
        'Excitation_729.rabi_excitation_amplitude':p.preparation_pulse_amplitude,
        'Excitation_729.rabi_excitation_phase':WithUnit(0,'deg')
        })
        evolution_pulse = TreeDict.fromdict({
        'Excitation_729.rabi_excitation_frequency':p.evolution_pulses_frequency,
        'Excitation_729.rabi_excitation_duration':p.evolution_pulses_duration,
        'Excitation_729.rabi_excitation_amplitude':p.evolution_pulses_amplitude,
        'Excitation_729.rabi_excitation_phase':p.evolution_pulses_phase                                               
        })
        rd = p.RamseyDephase
        heating_replace = TreeDict.fromdict({'Heating.local_blue_heating_frequency_397':rd.dephasing_frequency,
                                             'Heating.local_blue_heating_amplitude_397':rd.dephasing_amplitude,
                                             'Heating.blue_heating_frequency_866':p.StateReadout.state_readout_frequency_866,
                                             'Heating.blue_heating_amplitude_866': p.StateReadout.state_readout_amplitude_866,
                                             'Heating.blue_heating_duration':rd.dephasing_duration,
                                             'Heating.blue_heating_repump_additional':WithUnit(5, 'us')
                                             })
        #import IPython
        #IPython.embed()
        import boerge_tools
        print "First pulse:"
        boerge_tools.dump_keys(replace_preparation)
        print "Empty seq:"
        print p.evolution_ramsey_time
        print "Second Pulse:"
        boerge_tools.dump_keys(evolution_pulse)        
        
        self.addSequence(rabi_excitation, replacement_dict = replace_preparation)
        self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':p.evolution_ramsey_time}))
        self.addSequence(blue_heating, replace_preparation)
        if p.preparation_pulse_frequency == p.evolution_pulses_frequency:
            self.addSequence(rabi_excitation_no_offset, replacement_dict = evolution_pulse)
        else:
            self.addSequence(rabi_excitation, replacement_dict = evolution_pulse)
            
# class dephasing_pulses_old(pulse_sequence):
#     
#     required_parameters = [
#                            ('Dephasing_Pulses', 'preparation_pulse_frequency'),
#                            ('Dephasing_Pulses', 'preparation_pulse_duration'),
#                            ('Dephasing_Pulses', 'preparation_pulse_amplitude'),
#                            
#                            ('Dephasing_Pulses', 'evolution_pulses_frequency'),
#                            ('Dephasing_Pulses', 'evolution_pulses_duration'),
#                            ('Dephasing_Pulses', 'evolution_pulses_amplitude'),
#                            ('Dephasing_Pulses', 'evolution_ramsey_time'),
#                            ('Dephasing_Pulses', 'evolution_pulses_phase')
#                            ]
#     required_subsequences = [rabi_excitation, empty_sequence, rabi_excitation_no_offset]
#     replaced_parameters = {empty_sequence:[('EmptySequence','empty_sequence_duration')],
#                            rabi_excitation:[('Excitation_729','rabi_excitation_frequency'),
#                                             ('Excitation_729','rabi_excitation_phase'),
#                                             ('Excitation_729','rabi_excitation_amplitude'),
#                                             ('Excitation_729','rabi_excitation_duration'),
#                                             ],
#                             rabi_excitation_no_offset:[('Excitation_729','rabi_excitation_frequency'),
#                                             ('Excitation_729','rabi_excitation_phase'),
#                                             ('Excitation_729','rabi_excitation_amplitude'),
#                                             ('Excitation_729','rabi_excitation_duration'),
#                                             ]
#                            }
#                              
#     def sequence(self):
#         p = self.parameters.Dephasing_Pulses
#         replace_preparation = TreeDict.fromdict({
#         'Excitation_729.rabi_excitation_frequency':p.preparation_pulse_frequency,
#         'Excitation_729.rabi_excitation_duration':p.preparation_pulse_duration,
#         'Excitation_729.rabi_excitation_amplitude':p.preparation_pulse_amplitude,
#         'Excitation_729.rabi_excitation_phase':WithUnit(0,'deg')
#         })
#         self.addSequence(rabi_excitation, replacement_dict = replace_preparation)
#         evolution_pulse = TreeDict.fromdict({
#         'Excitation_729.rabi_excitation_frequency':p.evolution_pulses_frequency,
#         'Excitation_729.rabi_excitation_duration':p.evolution_pulses_duration,
#         'Excitation_729.rabi_excitation_amplitude':p.evolution_pulses_amplitude,
#         'Excitation_729.rabi_excitation_phase':p.evolution_pulses_phase                                               
#         })
#         self.addSequence(rabi_excitation_no_offset, replacement_dict = evolution_pulse)
#         self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':p.evolution_ramsey_time}))
#         evolution_pulse['Excitation_729.rabi_excitation_phase'] = p.evolution_pulses_phase + WithUnit(180,'deg')
#         self.addSequence(rabi_excitation_no_offset, replacement_dict = evolution_pulse)