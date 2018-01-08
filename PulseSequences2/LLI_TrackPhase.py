import numpy as np
from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import time


# Should find a better way to do this
detuning_1_global = U(0,'kHz') 
        
        
class TrackPhaseStateR(pulse_sequence):
    
    scannable_params = {   'LLI.phase': [(-90, 90.0, 180.0, 'deg'),'parity'],
                                                      
                        }
    # fixed parmas doesn't work -> you can declare fixed params for all the seq at the main class
#     fixed_params = {'StateReadout.readout_mode':'pmt'}
    def sequence(self):

        from LLI_StatePreparation import LLI_StatePreparation
        self.addSequence(LLI_StatePreparation)
              
    @classmethod
    def run_initial(cls,cxn, parameters_dict):
        print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')
        
    @classmethod
    def run_finally(cls, cxn, parameters_dict, all_data, Phase):
        

        
        print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)
        
        print " sequence ident" , int(cxn.scriptscanner.get_running()[0][0])  

        
        # for the multiple case we summ the probabilities, this also
        # reduces the dimension to 1 for single ion case 
        try:
            all_data = all_data.sum(1)
        except ValueError:
            return
        
        #print "139490834", freq_data, all_data
        
        detuning = None
        
        p = parameters_dict
        ramsey_time = p.LLI.wait_time
        
        ind1 = np.where(Phase == -90.0)
        ind2 = np.where(Phase == 90.0)
        
        p1 =all_data[ind1]
        p2 =all_data[ind2]
        
        detuning = 1.0*np.arccos(-(p1-p2))*180.0/np.pi
        
        
        
#         if not detuning:
#             detuning_1_global = None
#             print "4321"
#             ident = int(cxn.scriptscanner.get_running()[0][0])
#             print "stoping the sequence ident" , ident                     
#             cxn.scriptscanner.stop_sequence(ident)
#             return
        print "at ",Phase[ind1], " the pop is", p1  
        print "at ",Phase[ind2], " the pop is", p2
        print "wait time", ramsey_time," and the calculated phase", detuning, "in deg"
        
        # if we don't lost the ion or we don't have good readout than the detuning would be zero in this case we don't want to proccesd 
#         if detuning == 0.0:
#             
#             print "4321"
#             ident = int(cxn.scriptscanner.get_running()[0][0])
#             print "stoping the sequence ident" , ident                     
#             cxn.scriptscanner.stop_sequence(ident)
#             return
#         
#         detuning = U(detuning, "kHz")
        global detuning_1_global 
        detuning_1_global = detuning 
        
        

class TrackPhaseStateL(pulse_sequence):

    scannable_params = {'LLI.phase' : [(-90, 90, 180, 'deg'), 'parity']}
    # fixed parmas doesn't work -> you can declare fixed params for all the seq at the main class
    #fixed_params = {'StateReadout.readout_mode':'pmt'}

    def sequence(self):

        from LLI_StatePreparation import LLI_StatePreparation
        
        self.addSequence(LLI_StatePreparation, {"LLI.flip_optical_pumping": True}
                         )
        
    @classmethod
    def run_initial(cls,cxn, parameters_dict):
        print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')
        
    @classmethod
    def run_finally(cls, cxn, parameters_dict, all_data, Phase):
        
        print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)
        
        print " sequence ident" , int(cxn.scriptscanner.get_running()[0][0])  

        # Should find a better way to do this
        #global detuning_1_global 
        
        # for the multiple case we summ the probabilities, this also
        # reduces the dimension to 1 for single ion case 
        try:
            all_data = all_data.sum(1)
        except ValueError:
            return
                        
        p = parameters_dict
        ramsey_time = p.LLI.wait_time
        
        ind1 = np.where(Phase == -90.0)
        ind2 = np.where(Phase == 90.0)
        
        p1 =all_data[ind1]
        p2 =all_data[ind2]
        
        detuning_2 = 1.0*np.arccos(-(p1-p2))*180.0/np.pi #1.0*np.arcsin((p1-p2))*180.0/np.pi
        
        print "at ",Phase[ind1], " the pop is", p1  
        print "at ",Phase[ind2], " the pop is", p2
        print "wait time", ramsey_time," and the calculated phase", detuning_2, "in deg"
        
         
        
        
class LLI_TrackPhase(pulse_sequence):
    is_composite = True
    # at the moment fixed params are shared between the sub sequence!!! 
    fixed_params = {
                    }
    
    sequences = [TrackPhaseStateR, TrackPhaseStateL]


 

    show_params= [  "MolmerSorensen.due_carrier_enable",
                    "LLI.ms_carrier_1_line_selection",
                    "LLI.ms_carrier_2_line_selection",
                    "LLI.rotation_carrier_1_enable",
                    "LLI.rotation_carrier_1_line_selection",
                    "LLI.rotation_carrier_1_channel_729",
                    "LLI.pi_time_carrier_1",
                    "LLI.rotation_carrier_1_amplitude",
                    "LLI.rotation_carrier_2_enable",
                    "LLI.rotation_carrier_2_line_selection",
                    "LLI.rotation_carrier_2_channel_729",
                    "LLI.pi_time_carrier_2",
                    "LLI.rotation_carrier_2_amplitude",
                    "LLI.rotation_back_carrier_1_enable",
                    "LLI.rotation_back_carrier_2_enable",
                    "LLI.analysis_pulse_enable",
                    "LLI.pi_time_ms_carrier_1",
                    "LLI.ms_rotation_carrier_1_amplitude",
                    "LLI.pi_time_ms_carrier_2",
                    "LLI.ms_rotation_carrier_2_amplitude",   
                    "LLI.wait_time",
                    "LLI.analysis_pulse_duration", 
                    "LLI.flip_optical_pumping",
                    "LLI.fit_phase",                  
                      
                  ]
  
                  