from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
import time
from treedict import TreeDict
from scipy.optimize import curve_fit
import numpy as np




def fit_sin(phase,parity):
    
    model = lambda  x, a,  b,c: np.abs(a) * np.sin(( 2*np.deg2rad(x-b) ))+c
    p0=[0.5,0.0,0.0]
    
    # doesn't have bounds in the curve fit for this version so I mase the amplitude positive 
    #param_bounds=([-1.0,0,-1.0],[1.0,360,1.0])
    
    try:
        popt, copt = curve_fit(model, phase, parity, p0)
        print "best fit params" , popt
        print "contrast is " , popt[0]
        print "phase is  " , popt[1]
        phase_out=popt[1]
        return phase_out
    except:
        return None
        
   

def DataSort(All_data, num_of_ions):
    
    data_out=np.zeros([num_of_ions,len(All_data)])
    
    for i in range(len(All_data)):
        data_out[:,i]=All_data[i]
    return data_out

class LLI_StatePreparation(pulse_sequence):
    
                          
    scannable_params = { 'LLI.phase': [(0, 360.0, 15.0, 'deg'),'parity'],
                         'LLI.wait_time': [(0, 10.0, 0.1, 'ms'),'parity'] }

    fixed_params = {
                    'StateReadout.readout_mode': 'camera_parity'
                                        }
 

    show_params= [  "MolmerSorensen.due_carrier_enable",
                    "MolmerSorensen.bichro_enable",
                    "MolmerSorensen.gradient_shift",
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
                    "LLI.phase_offset",
                    "LLI.phase_offset_flipped_op",                 
                    "LLI.composite_rabi",
                    "LLI.simultaneous_rot",
                  ]
    
    @classmethod
    def run_initial(cls, cxn, parameters_dict):
        
#         print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')

        # Set up MS option       
        ms = parameters_dict.MolmerSorensen
        
        if ms.bichro_enable:
            # self.parameters['MolmerSorensen.frequency'] = freq_729
            #self.parameters['LocalRotation.frequency'] = freq_729
        
            # calc frequcy shift of the SP
            mode = ms.sideband_selection
            trap_frequency = parameters_dict['TrapFrequencies.' + mode]
        
#            print "Run initial to set the dds_cw freq"
#            print "Running ms gate trap freq is  ", trap_frequency
            # be carfull we are collecting the minus order from th SP
            # minus sign in the detuning getts closer to the carrier
            f_global = U(80.0, 'MHz') + U(0.15, 'MHz')
            freq_blue = f_global - trap_frequency - ms.detuning + ms.ac_stark_shift - ms.asymetric_ac_stark_shift
            freq_red = f_global + trap_frequency + ms.detuning  + ms.ac_stark_shift + ms.asymetric_ac_stark_shift
        
#            print "AC strak shift", ms.ac_stark_shift, " ms detuning ",ms.detuning 
#            print "MS freq_blue", freq_blue
#            print "MS freq_red  ", freq_red
        
            amp_blue = ms.amp_blue
            amp_red = ms.amp_red
        
            cxn.dds_cw.frequency('0', freq_blue)
            cxn.dds_cw.frequency('1', freq_red)
            cxn.dds_cw.frequency('2', f_global) # for driving the carrier
            cxn.dds_cw.amplitude('0', amp_blue)
            cxn.dds_cw.amplitude('1', amp_red)

            cxn.dds_cw.output('0', True)
            cxn.dds_cw.output('1', True)
            cxn.dds_cw.output('2', True)
        
        
            ampl_off = U(-63.0, 'dBm')
            cxn.dds_cw.amplitude('3',ampl_off )
            cxn.dds_cw.amplitude('4',ampl_off)
            cxn.dds_cw.output('3', False) # time to thermalize the single pass
            cxn.dds_cw.output('4', False) # time to thermalize the single pass
            cxn.dds_cw.output('5', True) # time to thermalize the single pass
            time.sleep(0.5)
        
            #cxn.dds_cw.output('5', False)
            time.sleep(0.5) # just make sure everything is programmed before starting the sequence

       

    @classmethod
    def run_finally(cls,cxn, parameters_dict, data, phase):
#        print "switching the 866 back to ON mode"
        cxn.pulser.switch_manual('866DP', True)
        parity = None 
        if parameters_dict.LLI.fit_phase:
#            print "fitting the parity to a sin curve: "
            all_data=np.array(data)
          
            if parameters_dict.StateReadout.readout_mode =='pmt_parity':
                #all_data = all_data.sum(1)
                all_data=DataSort(all_data,4)
                parity = all_data[-1,:]                                    
            elif parameters_dict.StateReadout.readout_mode =='camera_parity':
                num_of_ions=int(parameters_dict.IonsOnCamera.ion_number)
                all_data=DataSort(all_data,2*num_of_ions+1)
                parity = all_data[-1,:]
            
            if  parity== None:
                print "parity is none-> check StateReadout"  
            else:
                offset_phase=fit_sin(phase,parity)
#                print " offset_phase: ", offset_phase
                      
        
        
        
        
    def sequence(self):        
        from StatePreparation import StatePreparation
        from subsequences.Rotation import Rotation
        from subsequences.MolmerSorensen import MolmerSorensen
        from subsequences.StateReadout import StateReadout
        from subsequences.EmptySequence import EmptySequence
        from subsequences.TurnOffAll import TurnOffAll
        from subsequences.CompositeRabiExcitation import CompositeRabiExcitation
        from subsequences.RabiExcitation_2ions import RabiExcitation_2ions

        
        ms = self.parameters.MolmerSorensen
        lli = self.parameters.LLI
        
                       
        if  lli.flip_optical_pumping:
#            print "OPPOSITE optical pumping initial state is S-1/2S+1/2"
            op_line_selection = 'S-1/2D+3/2'
            op_aux_line_selection = 'S+1/2D-3/2'
            sbc_line_selection = 'S+1/2D+5/2'
            offset = lli.phase_offset_flipped_op
            
        else:
#            print "optical pumping initial state is S+1/2S-1/2"
            op_line_selection = self.parameters.OpticalPumping.line_selection
            op_aux_line_selection = self.parameters.OpticalPumpingAux.aux_op_line_selection
            sbc_line_selection = self.parameters.SidebandCooling.line_selection 
            offset = lli.phase_offset
        
        
        
        self.end = U(10., 'us')
        
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation, {"OpticalPumping.line_selection": op_line_selection,
                                            "OpticalPumpingAux.aux_op_line_selection": op_aux_line_selection,
                                            "SidebandCooling.line_selection": sbc_line_selection
                                            })     

        ## calculating the DP frquency 

        ms = self.parameters.MolmerSorensen

        ## calculating the DP frquency
        line1 = self.calc_freq(ms.line_selection)
        line2 = self.calc_freq(ms.line_selection_ion2)


######################################################
# changing to 2f2 and f1+f2 configuration
        freq_729_ms_carrier_2 = line2 + ms.detuning_carrier_2
        
        if ms.due_carrier_enable:
            if ms.use_alternate_DP_tones:
                freq_729_ms_carrier_1 =  ((2 * line1) - line2) + ms.detuning_carrier_1
                print "MS gate revised lines"
                
            else:
                freq_729_ms_carrier_1 =  line1 + ms.detuning_carrier_1
        
        else:
            freq_729_ms_carrier_1 = freq_729_ms_carrier_2    
        

        # freq_729_ms_carrier_1 = self.calc_freq(lli.ms_carrier_1_line_selection) 
        # freq_729_ms_carrier_2 = self.calc_freq(lli.ms_carrier_2_line_selection)



        # # Set up MS option
        # if ms.bichro_enable: 
        #     # Add gradient shift option
        #     if lli.flip_optical_pumping:
        #         freq_729_ms_carrier_1 = self.calc_freq(ms.line_selection) + ms.detuning_carrier_1 + ms.gradient_shift
        #     else:
        #         freq_729_ms_carrier_1 = self.calc_freq(ms.line_selection) + ms.detuning_carrier_1


        #     if ms.due_carrier_enable :
        #         # Add gradient shift option
        #         if lli.flip_optical_pumping:
        #             freq_729_ms_carrier_2 = self.calc_freq(ms.line_selection_ion2) + ms.detuning_carrier_2 - ms.gradient_shift
        #         else:
        #             if ms.use_alternate_DP_tones:
        #                 line1 = self.calc_freq(lli.ms_carrier_1_line_selection)
        #                 line2 = self.calc_freq(lli.ms_carrier_2_line_selection)
        #                 freq_729_ms_carrier_2 =  ((2 * line2) - line1) + ms.detuning_carrier_2
        #             else:
        #                 freq_729_ms_carrier_2 = self.calc_freq(ms.line_selection_ion2) + ms.detuning_carrier_2
        #     else:
        #         freq_729_ms_carrier_2 = freq_729        
 
       
         
        freq_729_rot1 = self.calc_freq(lli.rotation_carrier_1_line_selection) 
        freq_729_rot2 = self.calc_freq(lli.rotation_carrier_2_line_selection) 
        
        
#        print "Running ms Due gate DP freq is  ", freq_729_ms_carrier_1
#        print "Running ms Due gate DP freq for the second ion  is  ", freq_729_ms_carrier_2
        
        self.addSequence(MolmerSorensen, { 'MolmerSorensen.frequency': freq_729_ms_carrier_1,
                                           'MolmerSorensen.frequency_ion2': freq_729_ms_carrier_2
                                              })
        

        if lli.simultaneous_rot:
            print " Running pi times simultaneously"
            self.addSequence(RabiExcitation_2ions,{ "RabiFlopping_2ions.ion1_line_selection" : lli.rotation_carrier_1_line_selection,
                                                    "RabiFlopping_2ions.ion1_rabi_amplitude_729" : lli.rotation_carrier_1_amplitude,
                                                    "RabiFlopping_2ions.ion0_line_selection" : lli.rotation_carrier_2_line_selection,
                                                    "RabiFlopping_2ions.ion0_rabi_amplitude_729" : lli.rotation_carrier_2_amplitude,
                                                    "RabiFlopping_2ions.duration" : lli.pi_time_carrier_1,


                                                    } )
            
        else:
            if lli.rotation_carrier_1_enable:
            
             
                if lli.composite_rabi:
                    self.addSequence(CompositeRabiExcitation, {"Excitation_729.channel_729":lli.rotation_carrier_1_channel_729,
                                                           "Excitation_729.rabi_excitation_frequency":freq_729_rot1, 
                                                           "Excitation_729.rabi_excitation_duration":lli.pi_time_carrier_1,
                                                           "Excitation_729.rabi_excitation_amplitude":lli.rotation_carrier_1_amplitude,
                                                           "Excitation_729.rabi_excitation_phase": U(0, 'deg') 
                                                            })
            
                else:
                    self.addSequence(Rotation, {"Rotation.channel_729":lli.rotation_carrier_1_channel_729,
                                            "Rotation.frequency":freq_729_rot1, 
                                            "Rotation.pi_time":lli.pi_time_carrier_1,
                                            "Rotation.amplitude":lli.rotation_carrier_1_amplitude,
                                            "Rotation.angle": U(np.pi, 'rad') 
                                                   })
        
            if lli.rotation_carrier_2_enable:
           
             
                if lli.composite_rabi:
                    self.addSequence(CompositeRabiExcitation, {"Excitation_729.channel_729":lli.rotation_carrier_2_channel_729,
                                                           "Excitation_729.rabi_excitation_frequency":freq_729_rot2, 
                                                           "Excitation_729.rabi_excitation_duration":lli.pi_time_carrier_2,
                                                           "Excitation_729.rabi_excitation_amplitude":lli.rotation_carrier_2_amplitude,
                                                           "Excitation_729.rabi_excitation_phase": U(0, 'deg') 
                                                            })
                
            
            
                else:
                    self.addSequence(Rotation, {"Rotation.channel_729":lli.rotation_carrier_2_channel_729,
                                            "Rotation.frequency":freq_729_rot2, 
                                            "Rotation.pi_time":lli.pi_time_carrier_2,
                                            "Rotation.amplitude":lli.rotation_carrier_2_amplitude,
                                            "Rotation.angle": U(np.pi, 'rad') 
                                                   })



        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : lli.wait_time})
        
        #self.addSequence(Crystallization,  { "Crystallization.duration" : lli.wait_time})
        
        
        if lli.simultaneous_rot:
            self.addSequence(RabiExcitation_2ions,{ "RabiFlopping_2ions.ion1_line_selection" : lli.rotation_carrier_1_line_selection,
                                                    "RabiFlopping_2ions.ion1_rabi_amplitude_729" : lli.rotation_carrier_1_amplitude,
                                                    "RabiFlopping_2ions.ion0_line_selection" : lli.rotation_carrier_2_line_selection,
                                                    "RabiFlopping_2ions.ion0_rabi_amplitude_729" : lli.rotation_carrier_2_amplitude,
                                                    "RabiFlopping_2ions.duration" : lli.pi_time_carrier_1,


                                                    } )
            
        else:
            if lli.rotation_back_carrier_2_enable:
                        
            
                if lli.composite_rabi:
                    self.addSequence(CompositeRabiExcitation, {"Excitation_729.channel_729":lli.rotation_carrier_2_channel_729,
                                                           "Excitation_729.rabi_excitation_frequency":freq_729_rot2, 
                                                           "Excitation_729.rabi_excitation_duration":lli.pi_time_carrier_2,
                                                           "Excitation_729.rabi_excitation_amplitude":lli.rotation_carrier_2_amplitude,
                                                           "Excitation_729.rabi_excitation_phase": U(0, 'deg') 
                                                           })
            
                else:
                    self.addSequence(Rotation, {"Rotation.channel_729":lli.rotation_carrier_2_channel_729,
                                            "Rotation.frequency":freq_729_rot2, 
                                            "Rotation.pi_time":lli.pi_time_carrier_2,
                                            "Rotation.amplitude":lli.rotation_carrier_2_amplitude,
                                            "Rotation.angle": U(np.pi, 'rad') 
                                            })

        
            if lli.rotation_back_carrier_1_enable:
             
             
                if lli.composite_rabi:
                    self.addSequence(CompositeRabiExcitation, {"Excitation_729.channel_729":lli.rotation_carrier_1_channel_729,
                                                           "Excitation_729.rabi_excitation_frequency":freq_729_rot1, 
                                                           "Excitation_729.rabi_excitation_duration":lli.pi_time_carrier_1,
                                                           "Excitation_729.rabi_excitation_amplitude":lli.rotation_carrier_1_amplitude,
                                                           "Excitation_729.rabi_excitation_phase": U(0, 'deg') 
                                                           })
            
                else:
                    self.addSequence(Rotation, {"Rotation.channel_729":lli.rotation_carrier_1_channel_729,
                                            "Rotation.frequency":freq_729_rot1, 
                                            "Rotation.pi_time":lli.pi_time_carrier_1,
                                            "Rotation.amplitude":lli.rotation_carrier_1_amplitude,
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
                                               'MolmerSorensen.phase': lli.phase+offset,
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






