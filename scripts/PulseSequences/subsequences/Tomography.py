from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from StateReadout import state_readout
from RabiExcitation import rabi_excitation
from treedict import TreeDict
from labrad.units import WithUnit

class tomography_excitation(pulse_sequence):
    
    required_parameters = [ 
                           ('Tomography','rabi_pi_time'),
                           ('Tomography','iteration'),
                           ('Tomography','tomography_excitation_frequency'),
                           ('Tomography','tomography_excitation_amplitude'),
                          ]

    required_subsequences = [rabi_excitation]
    replaced_parameters = {
                           rabi_excitation:[
                                            ('Excitation_729','rabi_excitation_frequency'),
                                            ('Excitation_729','rabi_excitation_amplitude'),
                                            ('Excitation_729','rabi_excitation_duration'),
                                            ('Excitation_729','rabi_excitation_phase'),
                                            ]
                           }
    
    def sequence(self):
        t = self.parameters.Tomography
        iteration = int(t.iteration)
        if not iteration in range(3):
            raise Exception ("Incorrect iteration of tomography {}".format(iteration))
        if iteration == 0:
            pass
        elif iteration == 1:
            replace = TreeDict.fromdict({
                                        'Excitation_729.rabi_excitation_frequency':t.tomography_excitation_frequency,
                                        'Excitation_729.rabi_excitation_amplitude':t.tomography_excitation_amplitude,
                                        'Excitation_729.rabi_excitation_duration':t.rabi_pi_time / 2.0,
                                        'Excitation_729.rabi_excitation_phase':WithUnit(0, 'deg'),
                                        })
            self.addSequence(rabi_excitation, replace)
        elif iteration == 2:
            replace = TreeDict.fromdict({
                            'Excitation_729.rabi_excitation_frequency':t.tomography_excitation_frequency,
                            'Excitation_729.rabi_excitation_amplitude':t.tomography_excitation_amplitude,
                            'Excitation_729.rabi_excitation_duration':t.rabi_pi_time / 2.0,
                            'Excitation_729.rabi_excitation_phase':WithUnit(90, 'deg'),
                            })
            self.addSequence(rabi_excitation, replace)

class tomography_readout(pulse_sequence):
    '''
    pulse sequence that combines tomography rotations with the readout
    '''
    required_subsequences = [tomography_excitation, state_readout]
    
    def sequence(self):
        self.addSequence(tomography_excitation)
        self.addSequence(state_readout)