from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
import time
from treedict import TreeDict
import numpy as np




def fit_sin(phase,parity):
    from scipy.optimize import curve_fit
    
    model = lambda  x, a,  b,c: np.abs(a) * np.sin(( 2*np.deg2rad(x-b) ))+c
    p0=[0.5,0.0,0.0]
    
    # doesn't have bounds in the curve fit for this version so I mase the amplitude positive 
    #param_bounds=([-1.0,0,-1.0],[1.0,360,1.0])
    
    try:
        popt, copt = curve_fit(model, phase, parity, p0)
        print "best fit params" , popt
        print "contarst is " , popt[0]
        print "phase is  " , popt[1]
        phase_out=popt[1]
        return phase_out
    except:
        "wasn't able to fit this, pi time is set to the guess"
        return None
        
   

def DataSort(All_data, num_of_ions):
    
    data_out=np.zeros([num_of_ions,len(All_data)])
    
    for i in range(len(All_data)):
        data_out[:,i]=All_data[i]
    return data_out

class LLI_PhaseMeasurement(pulse_sequence):
    
                          
    scannable_params = {   'Dummy.dummy_detuning': [(0, 7.0, 1.0, 'deg'),'parity'],
                           
                        
                           #'MolmerSorensen.amplitude': [(-20, -10, 0.5, 'dBm'),'current'],
                           #'MolmerSorensen.phase': [(0, 360, 15, 'deg'),'parity']
                        }
    
    fixed_params = {
                    'StateReadout.readout_mode': 'pmt_parity'
                    
                    }

    show_params= [  "MolmerSorensen.due_carrier_enable",
                      
                    "LLI.wait_time",
                    "LLI.wait_time_long",
                    "LLI.phase_short_false",
                    "LLI.phase_short_true",
                    "LLI.phase_long_false",
                    "LLI.phase_long_true",
                                     
                      
                  ]
    
    @classmethod
    def run_initial(cls, cxn, parameters_dict):
        
        print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')
        ##################################################################################################
# Temporarily added this for MS
##################################################################################################        
        ms = parameters_dict.MolmerSorensen
        
        if ms.bichro_enable:
            print ""
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
            # time.sleep(0.5) # just make sure everything is programmed before starting the sequence
       



    @classmethod
    def run_finally(cls,cxn, parameters_dict, data, phase):
        print "switching the 866 back to ON mode"
        cxn.pulser.switch_manual('866DP', True)
#         parity = None 
#         if parameters_dict.LLI.fit_phase:
#             print "fitting the parity to a sin curve: "
#             all_data=np.array(data)
#           
#             if parameters_dict.StateReadout.readout_mode =='pmt_parity':
#                 #all_data = all_data.sum(1)
#                 all_data=DataSort(all_data,4)
#                 parity = all_data[-1,:]                                    
#             elif parameters_dict.StateReadout.readout_mode =='camera_parity':
#                 num_of_ions=int(parameters_dict.IonsOnCamera.ion_number)
#                 all_data=DataSort(all_data,2*num_of_ions+1)
#                 parity = all_data[-1,:]
#             
#             if  parity== None:
#                 print "parity is none-> check StateReadout"  
#             else:
#                 offset_phase=fit_sin(phase,parity)
#                 print " offset_phase: ", offset_phase
                      
        
        
        
        
    def sequence(self):        
        from StatePreparation import StatePreparation
        from subsequences.Rotation import Rotation
        from subsequences.MolmerSorensen import MolmerSorensen
        from subsequences.StateReadout import StateReadout
        from subsequences.EmptySequence import EmptySequence
        from subsequences.TurnOffAll import TurnOffAll
        from subsequences.Crystallization import Crystallization
        from subsequences.RabiExcitation_2ions import RabiExcitation_2ions
        
        ms = self.parameters.MolmerSorensen
        lli = self.parameters.LLI
        iter = self.parameters.Dummy.dummy_detuning
        iter = iter['deg']
        
        if iter ==0:
            wait_time = lli.wait_time
            flip_optical_pumping = False
            phase = U(0,'deg')+ lli.phase_short_false
            print 'short false 0 phase is', phase, 'deg'
        elif iter ==1:
            wait_time = lli.wait_time
            flip_optical_pumping = False
            phase = U(90,'deg')+ lli.phase_short_false

        elif iter ==2:
            wait_time = lli.wait_time_long
            flip_optical_pumping = False
            phase = U(0,'deg') + lli.phase_long_false
            print 'long false 0 phase is', phase, 'deg'
        elif iter ==3:
            wait_time = lli.wait_time_long
            flip_optical_pumping = False
            phase = U(90,'deg') + lli.phase_long_false
        if iter ==4:
            wait_time = lli.wait_time
            flip_optical_pumping = True
            phase = U(0,'deg') + lli.phase_short_true
            print 'short true 0 phase is', phase, 'deg'
        elif iter ==5:
            wait_time = lli.wait_time
            flip_optical_pumping = True
            phase = U(90,'deg') + lli.phase_short_true
        elif iter ==6:
            wait_time = lli.wait_time_long
            flip_optical_pumping = True
            phase = U(0,'deg') + lli.phase_long_true
            print 'long true 0 phase is', phase, 'deg'
        elif iter ==7:
            wait_time = lli.wait_time_long
            flip_optical_pumping = True
            phase = U(90,'deg')+ lli.phase_long_true
        elif iter ==8:
            wait_time = lli.wait_time
            flip_optical_pumping = False
            phase = U(45,'deg')+ lli.phase_short_false
        elif iter ==9:
            wait_time = lli.wait_time
            flip_optical_pumping = False
            phase = U(45+90,'deg')+ lli.phase_short_false
        
        print "iter #" , iter
        print wait_time , flip_optical_pumping, phase
                       
        if  flip_optical_pumping:
            print "OPPOSITE optical pumping initial state is S-1/2S+1/2"
            op_line_selection = 'S-1/2D+3/2'
            op_aux_line_selection = 'S+1/2D-3/2'
            sbc_line_selection = 'S+1/2D+5/2'
            
            
        else:
            print "optical pumping initial state is S+1/2S-1/2"
            op_line_selection = self.parameters.OpticalPumping.line_selection
            op_aux_line_selection = self.parameters.OpticalPumpingAux.aux_op_line_selection
            sbc_line_selection = self.parameters.SidebandCooling.line_selection 
            
        
        
        
        
        
        
        
        
        self.end = U(10., 'us')
        
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation, {"OpticalPumping.line_selection": op_line_selection,
                                            "OpticalPumpingAux.aux_op_line_selection": op_aux_line_selection,
                                            "SidebandCooling.line_selection": sbc_line_selection
                                            })     

#         ## calculating the DP frquency     
#         freq_729_ms_carrier_1=self.calc_freq(lli.ms_carrier_1_line_selection) 
#         freq_729_ms_carrier_2=self.calc_freq(lli.ms_carrier_2_line_selection) 
#         
        ##################################################################################################
# Temporarily added this for MS
##################################################################################################        
        
        if ms.bichro_enable: 
            freq_729_ms_carrier_1=self.calc_freq(ms.line_selection) + ms.detuning_carrier_1          
        
        
            if ms.due_carrier_enable :
                freq_729_ms_carrier_2=self.calc_freq(ms.line_selection_ion2) + ms.detuning_carrier_2
            else:
                freq_729_ms_carrier_2=freq_729
        else:
            ## calculating the DP frquency     
            freq_729_ms_carrier_1=self.calc_freq(lli.ms_carrier_1_line_selection) 
            freq_729_ms_carrier_2=self.calc_freq(lli.ms_carrier_2_line_selection) 
            
                
 
#############################################################################################################
#   Ends here
#############################################################################################################
        
        freq_729_rot1=self.calc_freq(lli.rotation_carrier_1_line_selection) 
        freq_729_rot2=self.calc_freq(lli.rotation_carrier_2_line_selection) 
        
        
        print "Running ms Due gate DP freq is  ", freq_729_ms_carrier_1
        print "Running ms Due gate DP freq for the second ion  is  ", freq_729_ms_carrier_2
        
        self.addSequence(MolmerSorensen, { 'MolmerSorensen.frequency': freq_729_ms_carrier_1,
                                           'MolmerSorensen.frequency_ion2': freq_729_ms_carrier_2,
                                           'MolmerSorensen.analysis_pulse_enable': False
                                              })
        

        if lli.simultaneous_rot:
            print " Running pi times simultaneously forward"
            self.addSequence(RabiExcitation_2ions,{ "RabiFlopping_2ions.ion1_line_selection" : lli.rotation_carrier_1_line_selection,
                                                    "RabiFlopping_2ions.ion1_rabi_amplitude_729" : lli.rotation_carrier_1_amplitude,
                                                    "RabiFlopping_2ions.ion0_line_selection" : lli.rotation_carrier_2_line_selection,
                                                    "RabiFlopping_2ions.ion0_rabi_amplitude_729" : lli.rotation_carrier_2_amplitude,
                                                    "RabiFlopping_2ions.duration" : lli.pi_time_carrier_1,


                                                    } )
            
        else:
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
        
        
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : wait_time})
        
        #self.addSequence(Crystallization,  { "Crystallization.duration" : lli.wait_time})
        
        if lli.simultaneous_rot:
            print " Running pi times simultaneously backward"
            self.addSequence(RabiExcitation_2ions,{ "RabiFlopping_2ions.ion1_line_selection" : lli.rotation_carrier_1_line_selection,
                                                    "RabiFlopping_2ions.ion1_rabi_amplitude_729" : lli.rotation_carrier_1_amplitude,
                                                    "RabiFlopping_2ions.ion0_line_selection" : lli.rotation_carrier_2_line_selection,
                                                    "RabiFlopping_2ions.ion0_rabi_amplitude_729" : lli.rotation_carrier_2_amplitude,
                                                    "RabiFlopping_2ions.duration" : lli.pi_time_carrier_1,


                                                    } )
            
        else:
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
                       
            
            self.addSequence(MolmerSorensen, { 'MolmerSorensen.frequency': freq_729_ms_carrier_1,
                                               'MolmerSorensen.frequency_ion2': freq_729_ms_carrier_2,
                                               'MolmerSorensen.phase': phase,
                                               'MolmerSorensen.bichro_enable': False,
                                               'MolmerSorensen.duration': lli.analysis_pulse_duration,
#                                                'MolmerSorensen.detuning': -1.0*trap_frequency,
                                               'MolmerSorensen.analysis_pulse_enable': False
                                              })
             
        

#             

        self.addSequence(StateReadout)






