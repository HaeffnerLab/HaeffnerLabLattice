from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import numpy as np


class CompositeRabiFlopping(pulse_sequence):
    scannable_params = {
        'RabiFlopping.duration':  [(0., 50., 3, 'us'), 'rabi'],
        'CompositeRabi.detuning':  [(-300., 300., 10., 'kHz'), 'spectrum']
              }

    show_params= ['Excitation_729.channel_729',
                  'Excitation_729.bichro',
                  'RabiFlopping.line_selection',
                  'RabiFlopping.rabi_amplitude_729',
                  'RabiFlopping.duration',
                  'RabiFlopping.rabi_amplitude_729',
                  'RabiFlopping.duration',
                  'RabiFlopping.line_selection',
                  'RabiFlopping.selection_sideband',
                  'RabiFlopping.order',
                  'StatePreparation.channel_729',
                  'StatePreparation.optical_pumping_enable',
                  'StatePreparation.sideband_cooling_enable',
                  'CompositeRabi.sequence_type',
                  'CompositeRabi.detuning'
                  ]
    

    def sequence(self):
        from StatePreparation import StatePreparation
        from subsequences.CompositeRabiExcitation import CompositeRabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
        
        ## calculate the scan params
        rf = self.parameters.RabiFlopping 
        detuning = self.parameters.CompositeRabi.detuning
        
        freq_729=self.calc_freq(rf.line_selection , rf.selection_sideband , rf.order) + detuning
        
        # building the sequence
        self.end = U(10., 'us')
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)
        self.addSequence(CompositeRabiExcitation,{'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': rf.rabi_amplitude_729,
                                         'Excitation_729.rabi_excitation_duration':  rf.duration })
        self.addSequence(StateReadout)
        
    @classmethod
    def run_initial(cls,cxn, parameters_dict):
#        print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')
        
    @classmethod
    def run_in_loop(cls,cxn, parameters_dict, data, x):
        #print "Running in loop Rabi_floping"
        pass
    @classmethod
    def run_finally(cls,cxn, parameters_dict, data, x):
#        print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)

        
