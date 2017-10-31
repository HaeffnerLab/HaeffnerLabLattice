from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import numpy as np

class RamseyLocalHanEcho(pulse_sequence):
    
    #name = 'Ramsey'

    scannable_params = {
                        
        'RamseyScanGap.ramsey_duration': [(0, 1.0, 0.5, 'ms') ,'ramsey'],
        'Ramsey.second_pulse_phase': [(0, 360., 15, 'deg') ,'ramsey']
        }

    show_params= ['RamseyScanGap.ramsey_duration',
                  'RamseyScanPhase.scanphase',
                  'RamseyScanGap.detuning',
                  
                  #need to work on this
                  'LocalRotation.amplitude',
                  'LocalRotation.pi_time',
                  
                  
                  'RabiFlopping.line_selection',
                  'RabiFlopping.selection_sideband',
                  'RabiFlopping.order',
                                                      
                  ]

    
    def sequence(self):
        
        from StatePreparation import StatePreparation
        from subsequences.LocalRotation import LocalRotation
        from subsequences.StateReadout import StateReadout
        from subsequences.EmptySequence import EmptySequence
        from subsequences.StateReadout import StateReadout
        
        
        
        ## calculate the 729 params
        rf = self.parameters.RabiFlopping   
        # calculating the 729 freq form the Rabi flop params
        freq_729=self.calc_freq(rf.line_selection , rf.selection_sideband , rf.order)
        # adding the Ramsey detuning
        freq_729 = freq_729+ self.parameters.RamseyScanGap.detuning
        
        print "1234"
        print " freq 729 " , freq_729
        print " Wait time ", self.parameters.RamseyScanGap.ramsey_duration
        
        # building the sequence
        self.addSequence(StatePreparation)            
        self.addSequence(LocalRotation, { "LocalRotation.frequency":freq_729,
                                           "LocalRotation.angle": U(np.pi/2.0, 'rad'),
                                           "LocalRotation.phase": U(0, 'deg')})
        
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : 0.5*self.parameters.RamseyScanGap.ramsey_duration})

        self.addSequence(LocalRotation, { "LocalRotation.frequency":freq_729,
                                           "LocalRotation.angle": U(np.pi/1.0, 'rad'),
                                           "LocalRotation.phase": U(0, 'deg')})
        
                
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : 0.5*self.parameters.RamseyScanGap.ramsey_duration})
        
        self.addSequence(LocalRotation, {"LocalRotation.frequency":freq_729, 
                                          "LocalRotation.angle": U(np.pi/2.0, 'rad'), 
                                          "LocalRotation.phase": self.parameters.Ramsey.second_pulse_phase })
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
