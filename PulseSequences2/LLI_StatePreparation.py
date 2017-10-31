from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
import time
from treedict import TreeDict
import numpy as np

#from subsequences.GlobalRotation import GlobalRotation
#from subsequences.LocalRotation import LocalRotation
#from subsequences.TurnOffAll import TurnOffAll

class LLI_StatePreparation(pulse_sequence):
    
                          
    scannable_params = {   'LLI.phase': [(0, 360.0, 15.0, 'deg'),'parity'],
                           'LLI.wait_time': [(0, 10.0, 0.1, 'ms'),'parity'],
                           #'MolmerSorensen.amplitude': [(-20, -10, 0.5, 'dBm'),'current'],
                           #'MolmerSorensen.phase': [(0, 360, 15, 'deg'),'parity']
                        }
 

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
                      
                  ]
    
    @classmethod
    def run_initial(cls, cxn, parameters_dict):
        
        print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')
        
#         ms = parameters_dict.MolmerSorensen
#         
#         # self.parameters['MolmerSorensen.frequency'] = freq_729
#         #self.parameters['LocalRotation.frequency'] = freq_729
#         
#         # calc frequcy shift of the SP
#         mode = ms.sideband_selection
#         trap_frequency = parameters_dict['TrapFrequencies.' + mode]
#         
#         print "4321"
#         print "Run initial to set the dds_cw freq"
#         print "Running ms gate trap freq is  ", trap_frequency
#         # be carfull we are collecting the minus order from th SP
#         # minus sign in the detuning getts closer to the carrier
#         f_global = U(80.0, 'MHz') + U(0.15, 'MHz')
#         freq_blue = f_global - trap_frequency - ms.detuning + ms.ac_stark_shift
#         freq_red = f_global + trap_frequency + ms.detuning  + ms.ac_stark_shift
#         
#         print "AC strak shift", ms.ac_stark_shift, " ms detuning ",ms.detuning 
#         print "MS freq_blue", freq_blue
#         print "MS freq_red  ", freq_red
#         
#         amp_blue = ms.amp_blue
#         amp_red = ms.amp_red
#         
#         cxn.dds_cw.frequency('0', freq_blue)
#         cxn.dds_cw.frequency('1', freq_red)
#         cxn.dds_cw.frequency('2', f_global) # for driving the carrier
#         cxn.dds_cw.amplitude('0', amp_blue)
#         cxn.dds_cw.amplitude('1', amp_red)
# 
#         cxn.dds_cw.output('0', True)
#         cxn.dds_cw.output('1', True)
#         cxn.dds_cw.output('2', True)
#         
#         cxn.dds_cw.output('5', True) # time to thermalize the single pass
#         time.sleep(1.0)
#         
#         #cxn.dds_cw.output('5', False)
#         time.sleep(0.5) # just make sure everything is programmed before starting the sequence

    @classmethod
    def run_finally(cls,cxn, parameters_dict, data, x):
        print "switching the 866 back to ON mode"
        cxn.pulser.switch_manual('866DP', True)
        
    def sequence(self):        
        from StatePreparation import StatePreparation
        from subsequences.Rotation import Rotation
        from subsequences.MolmerSorensen import MolmerSorensen
        from subsequences.StateReadout import StateReadout
        from subsequences.EmptySequence import EmptySequence
        from subsequences.TurnOffAll import TurnOffAll
        from subsequences.Crystallization import Crystallization
        
        ms = self.parameters.MolmerSorensen
        lli = self.parameters.LLI
        

        
        
        self.end = U(10., 'us')
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)     

        ## calculating the DP frquency     
        freq_729_ms_carrier_1=self.calc_freq(lli.ms_carrier_1_line_selection) 
        freq_729_ms_carrier_2=self.calc_freq(lli.ms_carrier_2_line_selection) 
        freq_729_rot1=self.calc_freq(lli.rotation_carrier_1_line_selection) 
        freq_729_rot2=self.calc_freq(lli.rotation_carrier_2_line_selection) 
        
        
        print "Running ms Due gate DP freq is  ", freq_729_ms_carrier_1
        print "Running ms Due gate DP freq for the second ion  is  ", freq_729_ms_carrier_2
        
        self.addSequence(MolmerSorensen, { 'MolmerSorensen.frequency': freq_729_ms_carrier_1,
                                           'MolmerSorensen.frequency_ion2': freq_729_ms_carrier_2
                                              })
        

        if lli.rotation_carrier_1_enable:
            
             
            #print "enabled rotation out "
            self.addSequence(Rotation, {"Rotation.channel_729":lli.rotation_carrier_1_channel_729,
                                        "Rotation.frequency":freq_729_rot1, 
                                        "Rotation.pi_time":lli.pi_time_carrier_1,
                                        "Rotation.amplitude":lli.rotation_carrier_1_amplitude,
                                        "Rotation.angle": U(np.pi, 'rad') 
                                               })
        
        if lli.rotation_carrier_2_enable:
           
             
            #print "enabled rotation out "
            self.addSequence(Rotation, {"Rotation.channel_729":lli.rotation_carrier_2_channel_729,
                                        "Rotation.frequency":freq_729_rot2, 
                                        "Rotation.pi_time":lli.pi_time_carrier_2,
                                        "Rotation.amplitude":lli.rotation_carrier_2_amplitude,
                                        "Rotation.angle": U(np.pi, 'rad') 
                                               })
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : lli.wait_time})
        
        #self.addSequence(Crystallization,  { "Crystallization.duration" : lli.wait_time})
        
        if lli.rotation_back_carrier_1_enable:
             
             
            #print "enabled rotation out "
            self.addSequence(Rotation, {"Rotation.channel_729":lli.rotation_carrier_1_channel_729,
                                        "Rotation.frequency":freq_729_rot1, 
                                        "Rotation.pi_time":lli.pi_time_carrier_1,
                                        "Rotation.amplitude":lli.rotation_carrier_1_amplitude,
                                        "Rotation.angle": U(np.pi, 'rad') 
                                               })
        
        if lli.rotation_back_carrier_2_enable:
                        
            
            self.addSequence(Rotation, {"Rotation.channel_729":lli.rotation_carrier_2_channel_729,
                                        "Rotation.frequency":freq_729_rot2, 
                                        "Rotation.pi_time":lli.pi_time_carrier_2,
                                        "Rotation.amplitude":lli.rotation_carrier_2_amplitude,
                                        "Rotation.angle": U(np.pi, 'rad') 
                                               })

        
        
        if lli.analysis_pulse_enable:
            # calc frequcy shift of the SP
            mode = ms.sideband_selection
            trap_frequency =  self.parameters.TrapFrequencies[mode]
            
            #print "1325"
            #print trap_frequency
            
            
            self.addSequence(MolmerSorensen, { 'MolmerSorensen.frequency': freq_729_ms_carrier_1,
                                               'MolmerSorensen.frequency_ion2': freq_729_ms_carrier_2,
                                               'MolmerSorensen.phase': lli.phase,
                                               'MolmerSorensen.bichro_enable': False,
                                               'MolmerSorensen.duration': lli.analysis_pulse_duration,
                                               'MolmerSorensen.detuning': -1.0*trap_frequency
                                              })
             
        
#             self.addSequence(Rotation, {"Rotation.channel_729": '729global',
#                                         "Rotation.frequency":freq_729_ms_carrier_1, 
#                                         "Rotation.pi_time":lli.pi_time_ms_carrier_1,
#                                         "Rotation.amplitude":lli.ms_rotation_carrier_1_amplitude,
#                                         "Rotation.angle": U(np.pi/2.0, 'rad'),
#                                         "Rotation.phase": lli.phase,
#                                         
#                                                })
#             
#             self.addSequence(Rotation, {"Rotation.channel_729": '729global_1',
#                                         "Rotation.frequency":freq_729_ms_carrier_2, 
#                                         "Rotation.pi_time":lli.pi_time_ms_carrier_2,
#                                         "Rotation.amplitude":lli.ms_rotation_carrier_2_amplitude,
#                                         "Rotation.angle": U(np.pi/2.0, 'rad'),
#                                         "Rotation.phase": lli.phase, 
#                                                })
#             
#             

        self.addSequence(StateReadout)






