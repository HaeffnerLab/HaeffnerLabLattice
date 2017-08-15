from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import numpy as np

class Ramsey(pulse_sequence):
    
    #name = 'Ramsey'

    scannable_params = {
        'RamseyScanGap.scangap': (0, 10.0, 0.1, 'ms'),
        'RamseyScanPhase.scanphase': (0, 360., 15, 'deg')
        }

    show_params= ['RamseyScanGap.scangap',
                  'RamseyScanPhase.scanphase',
                  'RamseyScanGap.detuning',
                  #need to work on this
                  'GlobalRotation.pi_time',
                  'RabiFlopping.line_selection',
                  'RabiFlopping.sideband_selection',
                  'sideband_order']

     
    def run_initial(self):
        pass
    
    
    def sequence(self):
        
        from StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        #from subsequences.TurnOffAll import TurnOffAll
        
        
        ## calculate the 729 params
        rf = self.parameters.RabiFlopping   
        
        if rf.selection_sideband == "off":         
            freq_729=self.calc_freq(rf.line_selection)
        else:
            freq_729=self.calc_freq(rf.line_selection, rf.selection_sideband ,int(rf.order))
        
        freq_729 = freq_729+ self.parameters.RamseyScanGap.detuning
        
        
        # building the sequence
        self.addSequence(StatePreparation)            
        self.addSequence(GlobalRotation, { "GlobalRotation.frequency":freq_729,
                                           "GlobalRotation.angle": np.pi/2.0,
                                           "GlobalRotation.phase": 0.0})
        
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : self.RamseyScanGap.scangap})
        
        self.addSequence(GlobalRotation, {"GlobalRotation.frequency":freq_729, 
                                          "GlobalRotation.angle": np.pi/2.0, 
                                          "GlobalRotation.phase": self.RamseyScanPhase.scanphase })
        self.addSequence(StateReadout)
        

#if __name__=='__main__':
#    #pv = TreeDict.fromdict({'DopplerCooling.duration':U(5, 'us')})
    #ex = Sequence(pv)
    #psw = pulse_sequence_wrapper('example.xml', pv)
#    print 'executing a scan gap'
#    Ramsey.execute_external(('Ramsey.ramsey_time', 0, 10.0, 0.1, 'ms'))
