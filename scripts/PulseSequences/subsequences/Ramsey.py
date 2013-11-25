from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from RabiExcitation import rabi_excitation, rabi_excitation_no_offset
from EmptySequence import empty_sequence
from treedict import TreeDict
from labrad.units import WithUnit

class ramsey_excitation(pulse_sequence):
    
    required_parameters = [ 
                           ('Ramsey','ramsey_time'),
                           ('Ramsey','first_pulse_duration'),
                           ('Ramsey','second_pulse_duration'),
                           ('Ramsey','second_pulse_phase'),
                          ]

    required_subsequences = [rabi_excitation, empty_sequence, rabi_excitation_no_offset]
    
    def sequence(self):
        r = self.parameters.Ramsey
        replace = TreeDict.fromdict({
                                     'Excitation_729.rabi_excitation_duration':r.first_pulse_duration,
                                     'Excitation_729.rabi_excitation_phase':WithUnit(0, 'deg'),
                                     })
        self.addSequence(rabi_excitation, replace)
        self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':r.ramsey_time}))
        replace = TreeDict.fromdict({
                             'Excitation_729.rabi_excitation_duration':r.second_pulse_duration,
                             'Excitation_729.rabi_excitation_phase':r.second_pulse_phase,
                             })
        self.addSequence(rabi_excitation_no_offset, replace)