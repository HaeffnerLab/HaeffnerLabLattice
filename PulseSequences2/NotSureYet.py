from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
import time
from treedict import TreeDict
import numpy as np

#from subsequences.GlobalRotation import GlobalRotation
#from subsequences.LocalRotation import LocalRotation
#from subsequences.TurnOffAll import TurnOffAll

class NotSureYet(pulse_sequence):
    
                          
    scannable_params = {'NSY.wait_time_1': [(0, 10.0, 0.1, 'ms'),'current'],
                        'NSY.wait_time_2': [(0, 10.0, 0.1, 'ms'),'current'],
                           #'MolmerSorensen.amplitude': [(-20, -10, 0.5, 'dBm'),'current'],
                           #'MolmerSorensen.phase': [(0, 360, 15, 'deg'),'parity']
                        }
 

    show_params= [  "NSY.rotation_carrier_line_selection",
                    "NSY.rotation_carrier_channel_729",                  
                    "NSY.pi_time",  
                    "NSY.wait_time_1",                  
                    "NSY.wait_time_2", 
                    "NSY.rotation_carrier_amplitude",
                  ]
    
    @classmethod
    def run_initial(cls, cxn, parameters_dict):
        
        print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')
 
    @classmethod
    def run_finally(cls,cxn, parameters_dict, data, x):
        print "switching the 866 back to ON mode"
        cxn.pulser.switch_manual('866DP', True)
        
    def sequence(self):        
        from StatePreparation import StatePreparation
        from subsequences.Rotation import Rotation
        from subsequences.StateReadout import StateReadout
        from subsequences.EmptySequence import EmptySequence
        from subsequences.TurnOffAll import TurnOffAll
        from subsequences.Crystallization import Crystallization
        
        nsy = self.parameters.NSY
        
        freq_729_rot=self.calc_freq(nsy.rotation_carrier_line_selection) 
             
        self.end = U(10., 'us')
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)     

        print "NSY params"
        print "freq is  ", freq_729_rot
        print "channel is  ", nsy.rotation_carrier_channel_729
        
        
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" :nsy.wait_time_1})
       
        print "2222"
            #print "enabled rotation out "
        self.addSequence(Rotation, {"Rotation.channel_729":nsy.rotation_carrier_channel_729,
                                    "Rotation.frequency":freq_729_rot, 
                                    "Rotation.pi_time":nsy.pi_time,
                                    "Rotation.amplitude":nsy.rotation_carrier_amplitude,
                                    "Rotation.angle": U(np.pi, 'rad') 
                                               })
        
        print "3333"
       
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" :nsy.wait_time_2})
        
        print "4444"
        
        self.addSequence(StateReadout)






