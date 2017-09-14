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
    
                          
    scannable_params = {   'MolmerSorensen.duration': [(0, 1.0, 0.1, 'ms'),'ms_time']
                        }
 

    show_params= [        'Excitation_729.channel_729',
                          'MolmerSorensen.duration',
                          'MolmerSorensen.line_selection',
                          'MolmerSorensen.frequency_selection',
                          'MolmerSorensen.sideband_selection',
                          'MolmerSorensen.detuning',
                          'MolmerSorensen.ac_stark_shift',
                          'MolmerSorensen.amp_red',
                          'MolmerSorensen.amp_blue',
                          'MolmerSorensen.analysis_pulse_enable',
                          'MolmerSorensen.SDDS_enable',
                          'MolmerSorensen.SDDS_rotate_out',
                    
                          'StatePreparation.channel_729',
                          'StatePreparation.optical_pumping_enable',
                          'StatePreparation.sideband_cooling_enable'
                  ]
    
    @classmethod
    def run_initial(cls, cxn, parameters_dict):
        
        ms = parameters_dict.MolmerSorensen
        
        # self.parameters['MolmerSorensen.frequency'] = freq_729
        #self.parameters['LocalRotation.frequency'] = freq_729
        
        # calc frequcy shift of the SP
        mode = ms.sideband_selection
        trap_frequency = parameters_dict['TrapFrequencies.' + mode]
        
        print "4321"
        print "Run initial to set the dds_cw freq"
        print "Running ms gate trap freq is  ", trap_frequency
        # be carfull we are collecting the minus order from th SP
        # minus sign in the detuning getts closer to the carrier
        f_global = U(80.0, 'MHz') + U(0.15, 'MHz')
        freq_blue = f_global - trap_frequency - ms.detuning + ms.ac_stark_shift
        freq_red = f_global + trap_frequency + ms.detuning  + ms.ac_stark_shift
        
        print "AC strak shift", ms.ac_stark_shift, " ms detuning ",ms.detuning 
        print "MS freq_blue", freq_blue
        print "MS freq_red  ", freq_red
        
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
        
        cxn.dds_cw.output('5', False)
        time.sleep(0.5) # just make sure everything is programmed before starting the sequence


    def sequence(self):        
        from StatePreparation import StatePreparation
        from subsequences.GlobalRotation import GlobalRotation
        from subsequences.LocalRotation import LocalRotation
        from subsequences.MolmerSorensen import MolmerSorensen
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
        
        p = self.parameters.MolmerSorensen
        

        ## calculating the DP frquency
        freq_729=self.calc_freq(p.line_selection)           
        print "Running ms gate DP freq is  ", freq_729

        
        self.end = U(10., 'us')
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)     

        if p.SDDS_enable:
            #print "1254"    
            #print "enabled rotation in "
            self.addSequence(LocalRotation, {"LocalRotation.frequency":freq_729, 
                                              "LocalRotation.angle": U(np.pi/2.0, 'rad') 
                                               })
  
        
        self.addSequence(MolmerSorensen, { 'MolmerSorensen.frequency': freq_729 })


        if p.SDDS_rotate_out:
            #print "enabled rotation out "
            self.addSequence(LocalRotation, {"LocalRotation.frequency":freq_729, 
                                              "LocalRotation.angle": U(np.pi/2.0, 'rad') 
                                               })
  
            
        
        if p.analysis_pulse_enable:
           
            self.addSequence(GlobalRotation, {"GlobalRotation.frequency":freq_729, 
                                              "GlobalRotation.angle": U(np.pi/2.0, 'rad'), 
                                              "GlobalRotation.phase": p.ms_phase })

        self.addSequence(StateReadout)






