from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict


class AuxOpticalPumpingOptimization(pulse_sequence):
                            
    scannable_params = {'OpticalPumpingAux.duration' : [(10., 200., 10., 'us'), 'current']
                        }

    show_params= ['OpticalPumpingAux.channel_729',
                  'OpticalPumpingAux.aux_op_line_selection',
                  'OpticalPumpingAux.aux_optical_pumping_amplitude_729',
                  
                  
                                   
                  'RabiFlopping.rabi_amplitude_729',
                  'RabiFlopping.duration',
                  'RabiFlopping.line_selection',
                  'RabiFlopping.selection_sideband',
                  'RabiFlopping.order',
                 ]
    
    
    def sequence(self):
        from StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
        
        
        ## calculate the scan params
        rf = self.parameters.RabiFlopping 
        freq_729=self.calc_freq(rf.line_selection , rf.selection_sideband , rf.order)
#         print "321321"
#         print "freq 729", freq_729 
        self.end = U(10., 'us')      
        
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)       
        self.addSequence(RabiExcitation,{'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': rf.rabi_amplitude_729,
                                         'Excitation_729.rabi_excitation_duration':  rf.duration })
        self.addSequence(StateReadout)
        
    @classmethod
    def run_initial(cls,cxn, parameters_dict):
        print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')
        
    @classmethod
    def run_in_loop(cls,cxn, parameters_dict, data, x):
        #print "Running in loop Rabi_floping"
        pass
    
    @classmethod
    def run_finally(cls,cxn, parameters_dict, data, x):
        print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)
        
        