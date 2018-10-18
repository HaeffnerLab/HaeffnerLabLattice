from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import numpy as np

class RamseyGlobalACStarkShiftEcho(pulse_sequence):
    
    #name = 'Ramsey'

    scannable_params = {
                        
        'RamseyScanGap.ramsey_duration': [(0, 1.0, 0.5, 'ms') ,'ramsey'],
        'LocalStarkShift.number_of_cycles': [(0, 10., 1, 'deg') ,'ramsey']
        }

    show_params= ['RamseyScanGap.ramsey_duration',
                  'RamseyScanPhase.scanphase',
                  'RamseyScanGap.detuning',
                  'Ramsey.second_pulse_phase',
                  #need to work on this
                  'GlobalRotation.amplitude',
                  'GlobalRotation.pi_time',

                  'LocalStarkShift.amplitude',
                  'LocalStarkShift.detuning',
                  'LocalStarkShift.number_of_cycles',


                  #'RabiFlopping.rabi_amplitude_729',
                  #'RabiFlopping.duration',
                  'RabiFlopping.line_selection',
                  'RabiFlopping.selection_sideband',
                  'RabiFlopping.order',
                                                      
                  ]

    
    def sequence(self):
        
        from StatePreparation import StatePreparation
        from subsequences.GlobalRotation import GlobalRotation
        from subsequences.StateReadout import StateReadout
        from subsequences.EmptySequence import EmptySequence
        from subsequences.RabiExcitation import RabiExcitation
        from Ramsey import Ramsey
        
        
        ## calculate the 729 params
        rf = self.parameters.RabiFlopping
        ra = self.parameters.Ramsey   

        wait_time = self.parameters.RamseyScanGap.ramsey_duration
        # calculating the 729 freq form the Rabi flop params
        freq_729=self.calc_freq(rf.line_selection , rf.selection_sideband , rf.order)
        # adding the Ramsey detuning
        
                

        print "1234"
        print " freq 729 " , freq_729
        print " Wait time ",  wait_time
        
        # building the sequence
        self.addSequence(StatePreparation)    

        #This is a pi/2 pulse without detuning        
        self.addSequence(GlobalRotation, { "GlobalRotation.frequency":freq_729,
                                           "GlobalRotation.angle": U(np.pi/2.0, 'rad'),
                                           "GlobalRotation.phase": U(0, 'deg')})
        
        # calculating the AC beam params from LocalStrakShift
        AC = self.parameters.LocalStarkShift
        
        N = int(AC.number_of_cycles['deg'])

        


        # for i in range(N):
        print " adding an ac strak shift cycle length N" , N
        print " ac strak shift freq" , freq_729 + AC.detuning

        if AC.detuning_sign_switch:
          for i in range(N):
            self.addSequence(RabiExcitation,{'Excitation_729.rabi_excitation_frequency': freq_729 + AC.detuning,
                                           'Excitation_729.rabi_excitation_amplitude': AC.amplitude,
                                           'Excitation_729.channel_729'              : '729global_1',
                                           'Excitation_729.rabi_excitation_duration':  wait_time/2.0 })

            self.addSequence(RabiExcitation,{'Excitation_729.rabi_excitation_frequency': freq_729 - AC.detuning,
                                           'Excitation_729.rabi_excitation_amplitude': AC.amplitude,
                                           'Excitation_729.channel_729'              : '729global_1',
                                           'Excitation_729.rabi_excitation_duration':  wait_time/2.0 })
        else:
          #Adding an AC Stark Shift surve as the purpose of the normal Ramsey detuning so the state vector will rotate
          self.addSequence(RabiExcitation,{'Excitation_729.rabi_excitation_frequency': freq_729 + AC.detuning,
                                         'Excitation_729.rabi_excitation_amplitude': AC.amplitude,
                                         'Excitation_729.channel_729'              : '729global_1',
                                         'Excitation_729.rabi_excitation_duration':  wait_time*N })        
        print "wait_time",wait_time 

        # if not ra.echo_enable

        # else:


        # #Pi/2 rotation around x
        # self.addSequence(GlobalRotation, {"GlobalRotation.frequency":freq_729, 
        #                                  "GlobalRotation.angle": U(np.pi/2.0, 'rad'), 
        # # 
        #                                  "GlobalRotation.phase": self.parameters.Ramsey.second_pulse_phase+U(np.pi/2.0,'rad') })
        
        # #Pi/2 for state read out
        self.addSequence(GlobalRotation, {"GlobalRotation.frequency":freq_729, 
                                         "GlobalRotation.angle": U(np.pi/2.0, 'rad'), 
                                         "GlobalRotation.phase": self.parameters.Ramsey.second_pulse_phase+U(np.pi/2.0,'rad') })
        
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

        

#if __name__=='__main__':
#    #pv = TreeDict.fromdict({'DopplerCooling.duration':U(5, 'us')})
    #ex = Sequence(pv)
    #psw = pulse_sequence_wrapper('example.xml', pv)
#    print 'executing a scan gap'
#    Ramsey.execute_external(('Ramsey.ramsey_time', 0, 10.0, 0.1, 'ms'))
