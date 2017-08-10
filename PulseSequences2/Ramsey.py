from common.devel.bum.sequences import pulse_sequence
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
        
        from PulseSequences2 import StatePreparation
        from PulseSequences2.subsequences import GlobalRotation
        from PulseSequences2.subsequences import EmptySequence 
        from PulseSequences2.subsequences import StateReadout
        
        ## calculate the 729 params
        carrier=self.parameters.RabiFlopping.line_selection
        side_band=self.parameters.RabiFlopping.sideband_selection
        order=self.parameters.RabiFlopping.sideband_order 
        freq_729 = self.calc_freq(carrier, side_band,order)  
        ramsey_detuning= self.parameters.RamseyScanGap.detuning 
        freq_729 = freq_729+ramsey_detuning          
        
        # building the sequence
        self.addSequence(StatePreparation)            
        self.addSequence(GlobalRotation, { "GlobalRotation.frequency":freq_729,
                                           "GlobalRotation.angle": np.pi/2.0,
                                           "GlobalRotation.phase": 0.0})
        
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : self.Ramsey.ramsey_time})
        
        self.addSequence(GlobalRotation, {"GlobalRotation.frequency":freq_729, 
                                          "GlobalRotation.angle": np.pi/2.0, 
                                          "GlobalRotation.phase": self.Ramsey.second_pulse_phase })
        self.addSequence(StateReadout)
        

if __name__=='__main__':
    #pv = TreeDict.fromdict({'DopplerCooling.duration':U(5, 'us')})
    #ex = Sequence(pv)
    #psw = pulse_sequence_wrapper('example.xml', pv)
    print 'executing a scan gap'
    Ramsey.execute_external(('Ramsey.ramsey_time', 0, 10.0, 0.1, 'ms'))
