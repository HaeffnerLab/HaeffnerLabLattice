from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
import time
from treedict import TreeDict
import numpy as np

#from subsequences.GlobalRotation import GlobalRotation
#from subsequences.LocalRotation import LocalRotation
#from subsequences.TurnOffAll import TurnOffAll

class MolmerSorensenGateWithEcho(pulse_sequence):
    
                          
    scannable_params = {   'MolmerSorensen.duration': [(0,200.0, 10.0, 'us'),'ms_time'],
                           'MolmerSorensen.amplitude': [(-20, -10, 0.5, 'dBm'),'ms_time'],
#                            'MolmerSorensen.phase': [(0, 360, 15, 'deg'),'parity'],
                           'MolmerSorensen.detuning_carrier_1': [(-10.0, 10, 0.5, 'kHz'),'ms_time'],
                           'MolmerSorensen.detuning_carrier_2': [(-10.0, 10, 0.5, 'kHz'),'ms_time'],
                           'MolmerSorensen.ms_phase': [(0, 360, 15, 'deg'),'parity'],
                           'MolmerSorensen.echo_time': [(0,200.0, 10.0, 'us'),'ms_time'],
                           
                           }
 

    show_params= [        
                          'MolmerSorensen.duration',
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
                          'MolmerSorensen.echo_enable',
                          'MolmerSorensen.echo_time',
                          
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
        
        cxn.dds_cw.frequency('0', freq_blue)
        cxn.dds_cw.frequency('1', freq_red)
        cxn.dds_cw.frequency('2', f_global) # for driving the carrier
        cxn.dds_cw.amplitude('0', amp_blue)
        cxn.dds_cw.amplitude('1', amp_red)

        cxn.dds_cw.output('0', True)
        cxn.dds_cw.output('1', True)
        cxn.dds_cw.output('2', True)
        
        cxn.dds_cw.output('5', True) # time to thermalize the single pass
        time.sleep(1.0)
        
        #cxn.dds_cw.output('5', False)
        time.sleep(0.5) # just make sure everything is programmed before starting the sequence

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
        from subsequences.EmptySequence import EmptySequence
        
        p = self.parameters.MolmerSorensen
        

        ## calculating the DP frquency
        freq_729=self.calc_freq(p.line_selection) + p.detuning_carrier_1          
        
        
        if p.due_carrier_enable :
            freq_729_ion2=self.calc_freq(p.line_selection_ion2) + p.detuning_carrier_2
        else:
            freq_729_ion2=freq_729
        
#         print "Running ms gate", p.line_selection, " DP freq is  ", freq_729
#         print "Running ms gate", p.line_selection_ion2, " DP freq is  ", freq_729_ion2
        
        
        self.end = U(10., 'us')
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)     

        if p.SDDS_enable:

            self.addSequence(LocalRotation, {"LocalRotation.frequency":freq_729, 
                                             "LocalRotation.angle": U(np.pi, 'rad') 
                                               })
        #add an echo in between each scanned duration MS/2 -> Pi -> MS/2
        if not p.echo_enable:
            self.addSequence(MolmerSorensen, { 'MolmerSorensen.frequency': freq_729,
                                               'MolmerSorensen.frequency_ion2': freq_729_ion2,
                                               })
        else:
            
            self.addSequence(MolmerSorensen, { 'MolmerSorensen.frequency': freq_729,
                                               'MolmerSorensen.frequency_ion2': freq_729_ion2,
                                               'MolmerSorensen.duration': p.duration/2.0,
                                               })     
            
            self.addSequence(GlobalRotation,{"GlobalRotation.frequency":freq_729, 
                                            "GlobalRotation.angle": U(np.pi, 'rad') 
                                               })   

            self.addSequence(MolmerSorensen, { 'MolmerSorensen.frequency': freq_729,
                                               'MolmerSorensen.frequency_ion2': freq_729_ion2,
                                               'MolmerSorensen.duration': p.duration/2.0,
                                               })


        if p.SDDS_rotate_out:
            #print "enabled rotation out "
            self.addSequence(LocalRotation, {"LocalRotation.frequency":freq_729, 
                                             "LocalRotation.angle": U(np.pi, 'rad') 
                                               })
  
            
        # if p.echo_enable:
        #            # self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : p.echo_time})
        #            self.addSequence(GlobalRotation,{"GlobalRotation.frequency":freq_729, 
        #                                              "GlobalRotation.angle": U(np.pi, 'rad') 
        #                                        })

        #            self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : p.duration})

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
                                                   'MolmerSorensen.amplitude': p.analysis_amplitude,
                                                   'MolmerSorensen.detuning': -1.0*trap_frequency}) 

            else:
                # calc frequcy shift of the SP
                 
               
            
            
                self.addSequence(MolmerSorensen, { 'MolmerSorensen.frequency': freq_729,
                                                   'MolmerSorensen.frequency_ion2': freq_729_ion2,
                                                   'MolmerSorensen.phase': p.ms_phase,
                                                   'MolmerSorensen.bichro_enable': False,
                                                   'MolmerSorensen.duration': p.analysis_duration,
                                                   'MolmerSorensen.detuning': -1.0*trap_frequency
                                                  })
             
        
        
        self.addSequence(StateReadout)






