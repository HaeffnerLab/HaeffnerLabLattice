from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from RabiExcitation import rabi_excitation, rabi_excitation_no_offset
from BlueHeating import local_blue_heating
from EmptySequence import empty_sequence
from treedict import TreeDict
from labrad.units import WithUnit

class ramsey_dephase_excitation(pulse_sequence):
    
    required_parameters = [ 
                           ('Ramsey','rabi_pi_time'),
                           ('RamseyDephase','pulse_gap'),
                           ('RamseyDephase','dephasing_frequency'),
                           ('RamseyDephase','dephasing_amplitude'),
                           ('RamseyDephase','dephasing_duration'),
                           ('RamseyDephase','second_pulse_duration'),
                           ('StateReadout','state_readout_frequency_866'), 
                           ('StateReadout','state_readout_amplitude_866'), 
                          ]

    required_subsequences = [rabi_excitation, empty_sequence, rabi_excitation_no_offset, local_blue_heating]
    
    def sequence(self):
        p = self.parameters
        spacing = (p.RamseyDephase.pulse_gap - p.RamseyDephase.dephasing_duration) / 2.0
        heating_replace = TreeDict.fromdict({'Heating.local_blue_heating_frequency_397':p.RamseyDephase.dephasing_frequency,
                                             'Heating.local_blue_heating_amplitude_397':p.RamseyDephase.dephasing_amplitude,
                                             'Heating.blue_heating_frequency_866':p.StateReadout.state_readout_frequency_866,
                                             'Heating.blue_heating_amplitude_866': p.StateReadout.state_readout_amplitude_866,
                                             'Heating.blue_heating_duration':p.RamseyDephase.dephasing_duration,
                                             'Heating.blue_heating_repump_additional':WithUnit(5, 'us')
                                             })
        if spacing < WithUnit(10.0, 'us'): raise Exception("Ramsey Dephase, gap is too short to accomodate dephasing")
        self.addSequence(rabi_excitation, TreeDict.fromdict({'Excitation_729.rabi_excitation_duration':p.Ramsey.rabi_pi_time / 2.0}))
        self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':spacing}))
        self.addSequence(local_blue_heating, heating_replace)
        self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':spacing}))
        self.addSequence(rabi_excitation_no_offset, TreeDict.fromdict({'Excitation_729.rabi_excitation_duration':p.RamseyDephase.second_pulse_duration}))