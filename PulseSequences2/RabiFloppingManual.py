from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict

class RabiFloppingManual(pulse_sequence):
    
    name = 'RabiFloppingManual'
                            #(self, scan_param, minim, maxim, steps, unit)
    scannable_params = {
        'Excitation_729.rabi_excitation_duration':  [(0., 50., 2, 'us'), 'rabi'],
        'Excitation_729.rabi_excitation_frequency':  [(-30, 30., 10, 'MHz'), 'spectrum']
        #'RabiFlopping.manual_scan':  [(0., 50., 2, 'us'), 'rabi']
              }

    show_params= ['Excitation_729.channel_729',
                  'Excitation_729.bichro',
                  'Excitation_729.rabi_excitation_amplitude',
                  'StateReadout.threshold_list'
                  ]
    
    def sequence(self):
        from StatePreparation import StatePreparation
        from subsequences.RabiExcitationManual import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
        
        # building the sequence
        self.end = U(10., 'us')
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)
        self.addSequence(RabiExcitation)     
        #self.addSequence(RabiExcitation,{'Excitation_729.rabi_excitation_frequency': freq_729,
        #                                 'Excitation_729.rabi_excitation_amplitude': rf.rabi_amplitude_729,
        #                                 'Excitation_729.rabi_excitation_duration':  rf.duration })
        self.addSequence(StateReadout)