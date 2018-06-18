from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
import time
from treedict import TreeDict
import numpy as np

#from subsequences.GlobalRotation import GlobalRotation
#from subsequences.LocalRotation import LocalRotation
#from subsequences.TurnOffAll import TurnOffAll

class MolmerSorensenGate(pulse_sequence):
    
                          
    scannable_params = {   'MolmerSorensen.duration': [(0,200.0, 10.0, 'us'),'ms_time'],
                           'MolmerSorensen.amplitude': [(-20, -10, 0.5, 'dBm'),'ms_time'],
#                            'MolmerSorensen.phase': [(0, 360, 15, 'deg'),'parity'],
                           'MolmerSorensen.detuning_carrier_1': [(-10.0, 10, 0.5, 'kHz'),'ms_time'],
                           'MolmerSorensen.detuning_carrier_2': [(-10.0, 10, 0.5, 'kHz'),'ms_time'],
                           'MolmerSorensen.ms_phase': [(0, 360, 15, 'deg'),'parity'],
                           'MolmerSorensen.asymetric_ac_stark_shift': [(-2.0, 2.0, 0.1, 'kHz'),'ms_time'],
                           # "MolmerSorensen.amp_red": [(-20, -10, 0.5, "dBm"), "ms_time"],
                           # "MolmerSorensen.amp_blue": [(-20, -10, 0.5, "dBm"), "ms_time"],
                           # 'MolmerSorensen.freq_blue': [(-2.0, 2.0, 0.1, 'kHz'),'ms_time'],
                           # 'MolmerSorensen.freq_red': [(-2.0, 2.0, 0.1, 'kHz'),'ms_time']
                           #"MolmerSorensen.sim_bichro_scan": [(-4, 4, 0.01, "dBm"), "ms_time"]
                        }
 

    show_params= ['MolmerSorensen.duration',
                  'MolmerSorensen.line_selection',
                  'MolmerSorensen.line_selection_ion2',
                  'MolmerSorensen.due_carrier_enable',
                  'MolmerSorensen.sideband_selection',
                  'MolmerSorensen.detuning',
                  'MolmerSorensen.ac_stark_shift',
                  'MolmerSorensen.asymetric_ac_stark_shift',
                  'MolmerSorensen.amp_red',
                  'MolmerSorensen.amp_blue',
                  'MolmerSorensen.amplitude',
                  'MolmerSorensen.amplitude_ion2',
                  'MolmerSorensen.analysis_pulse_enable',
                  'MolmerSorensen.SDDS_enable',
                  'MolmerSorensen.SDDS_rotate_out',
                  'MolmerSorensen.shape_profile',
                  'MolmerSorensen.bichro_enable',
                  'MolmerSorensen.carrier_1',
                  'MolmerSorensen.carrier_2',
                  'MolmerSorensen.analysis_duration',
                  'MolmerSorensen.flip_optical_pumping',
                  "MolmerSorensen.use_alternate_DP_tones",
                  "MolmerSorensen.two_pulses",
                  "MolmerSorensen.enable_DD",
                  "MolmerSorensen.analysis_amplitude",
                  "MolmerSorensen.analysis_amplitude_ion2",
                  "MolmerSorensen.use_analysis_amplitudes",
                  "MolmerSorensen.freq_blue",
                  "MolmerSorensen.freq_red"
                ]
    
    @classmethod
    def run_initial(cls, cxn, parameters_dict):
        
#         print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')
        
        ms = parameters_dict.MolmerSorensen
        
        # self.parameters['MolmerSorensen.frequency'] = freq_729
        #self.parameters['LocalRotation.frequency'] = freq_729
        
        # calc frequcy shift of the SP
        mode = ms.sideband_selection
        trap_frequency = parameters_dict['TrapFrequencies.' + mode]
        
#         print "4321"
#         print "Run initial to set the dds_cw freq"
#         print "Running ms gate trap freq is  ", trap_frequency
        # be carfull we are collecting the minus order from th SP
        # minus sign in the detuning getts closer to the carrier
        f_global = U(80.0, 'MHz') + U(0.15, 'MHz')
        freq_blue = f_global - trap_frequency - ms.detuning + ms.ac_stark_shift - ms.asymetric_ac_stark_shift
        freq_red = f_global + trap_frequency + ms.detuning  + ms.ac_stark_shift + ms.asymetric_ac_stark_shift
        
#         print "AC strak shift", ms.ac_stark_shift, " ms detuning ",ms.detuning 
#         print "MS freq_blue", freq_blue
#         print "MS freq_red  ", freq_red
        
        amp_blue = ms.amp_blue
        amp_red = ms.amp_red
        
        cxn.dds_cw.frequency('0', freq_blue + ms.freq_blue)
        cxn.dds_cw.frequency('1', freq_red + ms.freq_red)
        cxn.dds_cw.frequency('2', f_global) # for driving the carrier
        cxn.dds_cw.amplitude('0', amp_blue + ms.sim_bichro_scan)
        cxn.dds_cw.amplitude('1', amp_red - ms.sim_bichro_scan)

        cxn.dds_cw.output('0', True)
        cxn.dds_cw.output('1', True)
        cxn.dds_cw.output('2', True)
        
        cxn.dds_cw.output('5', True) # time to thermalize the single pass
        time.sleep(1.0)
        
        #cxn.dds_cw.output('5', False)
        time.sleep(0.5) # just make sure everything is programmed before starting the sequence
    
    @classmethod
    def run_in_loop(cls, cxn, parameters_dict, data_so_far,data_x):
      pass
        # ms = parameters_dict.MolmerSorensen
        
        # # self.parameters['MolmerSorensen.frequency'] = freq_729
        # #self.parameters['LocalRotation.frequency'] = freq_729
        
        # # calc frequcy shift of the SP
        # mode = ms.sideband_selection
        # trap_frequency = parameters_dict['TrapFrequencies.' + mode]

        # f_global = U(80.0, 'MHz') + U(0.15, 'MHz')
        # freq_blue = f_global - trap_frequency - ms.detuning + ms.ac_stark_shift - ms.asymetric_ac_stark_shift
        # freq_red = f_global + trap_frequency + ms.detuning  + ms.ac_stark_shift + ms.asymetric_ac_stark_shift

        # print "scanning in loop"
        # print "ms freq_blue ", ms.freq_blue
        # cxn.dds_cw.frequency('0', freq_blue + ms.freq_blue)
        # cxn.dds_cw.frequency('1', freq_red + ms.freq_red)
        # time.sleep(0.5)
        # print " dds_cw freq 0" , cxn.dds_cw.frequency('0')
        # print " dds_cw freq 1" , cxn.dds_cw.frequency('1')
        # cxn.dds_cw.amplitude('0', ms.amp_blue + ms.sim_bichro_scan)
        # cxn.dds_cw.amplitude('1', ms.amp_red - ms.sim_bichro_scan)




    @classmethod
    def run_finally(cls,cxn, parameters_dict, data, x):
#         print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)
        
    def sequence(self):        
        from StatePreparation import StatePreparation
        from subsequences.GlobalRotation import GlobalRotation
        from subsequences.LocalRotation import LocalRotation
        from subsequences.MolmerSorensen import MolmerSorensen
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
        from subsequences.RabiExcitation import RabiExcitation
        
        
        p = self.parameters.MolmerSorensen

        ## calculating the DP frquency
        line1 = self.calc_freq(p.line_selection)
        line2 = self.calc_freq(p.line_selection_ion2)


######################################################
# changing to 2f2 and f1+f2 configuration
        freq_729_ion2 = line2 + p.detuning_carrier_2
        
        if p.due_carrier_enable:
            if p.use_alternate_DP_tones:
                freq_729 =  ((2 * line1) - line2) + p.detuning_carrier_1
                print "MS gate revised lines"
                
            else:
                freq_729 =  line1 + p.detuning_carrier_1
        
        else:
            freq_729 = freq_729_ion2
        # print " 5555"
        # print "MS lines :"
        # print "line1  ",line1," freq_729" , freq_729
        # print "line2  ",line2," freq_729_ion2" , freq_729_ion2
        # print "0.5*(f1+f2)", 0.5*(freq_729+freq_729_ion2)

###################################################

        # freq_729 = line1 + p.detuning_carrier_1
        
        # if p.due_carrier_enable:
        #     if p.use_alternate_DP_tones:
        #         freq_729_ion2 =  ((2 * line2) - line1) + p.detuning_carrier_2
        #         print "Here we are"
        #     else:
        #         freq_729_ion2 =  line2 + p.detuning_carrier_2
        
        # else:
        #     freq_729_ion2 = freq_729
        
        

########################################################################################################
# add flip optical pumping option
########################################################################################################

        if  self.parameters.lli.flip_optical_pumping:
#            print "OPPOSITE optical pumping initial state is S-1/2S+1/2"
            op_line_selection = 'S-1/2D+3/2'
            op_aux_line_selection = 'S+1/2D-3/2'
            sbc_line_selection = 'S+1/2D+5/2'
            
        else:
#            print "optical pumping initial state is S+1/2S-1/2"
            op_line_selection = self.parameters.OpticalPumping.line_selection
            op_aux_line_selection = self.parameters.OpticalPumpingAux.aux_op_line_selection
            sbc_line_selection = self.parameters.SidebandCooling.line_selection 

########################################################################################################

        
        self.end = U(10., 'us')
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation, {"OpticalPumping.line_selection": op_line_selection,
                                            "OpticalPumpingAux.aux_op_line_selection": op_aux_line_selection,
                                            "SidebandCooling.line_selection": sbc_line_selection
                                            })     

        if not p.enable_DD:

            if p.SDDS_enable:

                self.addSequence(LocalRotation, {"LocalRotation.frequency":freq_729, 
                                                 "LocalRotation.angle": U(np.pi, 'rad') 
                                                   })
      
            

            self.addSequence(MolmerSorensen, { 'MolmerSorensen.frequency': freq_729,
                                               'MolmerSorensen.frequency_ion2': freq_729_ion2,
                                              
                                               })


            if p.SDDS_rotate_out:
                #print "enabled rotation out "
                self.addSequence(LocalRotation, {"LocalRotation.frequency":freq_729, 
                                                 "LocalRotation.angle": U(np.pi, 'rad') 
                                                   })
        else:

            N = int(p.num_DD_pulses)

            for _ in range(N):

                self.addSequence(MolmerSorensen, {"MolmerSorensen.frequency": freq_729,
                                                  "MolmerSorensen.frequency_ion2": freq_729_ion2,
                                                  "MolmerSorensen.duration": p.duration/(N+1)})

                self.addSequence(RabiExcitation, {"Excitation_729.rabi_excitation_frequency": line1,
                                                  "Excitation_729.rabi_excitation_duration": p.analysis_duration*2,
                                                  "Excitation_729.rabi_excitation_amplitude": p.analysis_amplitude,
                                                  "Excitation_729.channel_729": "729global_2",
                                                  "Excitation_729.phase_792": U(180.0, "deg")})

            self.addSequence(MolmerSorensen, {"MolmerSorensen.frequency": freq_729,
                                              "MolmerSorensen.frequency_ion2": freq_729_ion2,
                                              "MolmerSorensen.duration": p.duration/(N+1)})

  
            
        
        if p.analysis_pulse_enable:
            mode = p.sideband_selection
            trap_frequency =  self.parameters.TrapFrequencies[mode]    
            if not p.due_carrier_enable:
#                 self.addSequence(GlobalRotation, {"GlobalRotation.frequency":freq_729, 
#                                                   "GlobalRotation.angle": U(np.pi/2.0, 'rad'), 
#                                                   "GlobalRotation.phase": p.ms_phase })

                self.addSequence(MolmerSorensen, { 'MolmerSorensen.frequency': freq_729,
                                                   'MolmerSorensen.frequency_ion2': freq_729,
                                                   'MolmerSorensen.phase': p.ms_phase,
                                                   'MolmerSorensen.bichro_enable': False,
                                                   'MolmerSorensen.duration': p.analysis_duration,
                                                   'MolmerSorensen.detuning': -1.0*trap_frequency,
                                                   "MolmerSorensen.amplitude": p.analysis_amplitude}) 

            else:
                # calc frequcy shift of the SP
                 
               
            
            
                self.addSequence(MolmerSorensen, { 'MolmerSorensen.frequency': freq_729,
                                                   'MolmerSorensen.frequency_ion2': freq_729_ion2,
                                                   'MolmerSorensen.phase': p.ms_phase,
                                                   'MolmerSorensen.bichro_enable': False,
                                                   'MolmerSorensen.duration': p.analysis_duration,
                                                   'MolmerSorensen.detuning': -1.0*trap_frequency,
                                                   "MolmerSorensen.amplitude": p.analysis_amplitude,
                                                   "MolmerSorensen.amplitude_ion2": p.analysis_amplitude_ion2
                                                  })
             
        
        
        self.addSequence(StateReadout)






