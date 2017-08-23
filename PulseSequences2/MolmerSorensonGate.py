from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
from subsequences.MolmerSorensen import MolmerSorensen
from subsequences.GlobalRotation import GlobalRotation
from subsequences.LocalRotation import LocalRotation
from subsequences.TurnOffAll import TurnOffAll

class MolmerSorensonGate(pulse_sequence):
    
                          
    scannable_params = {   duration: : (0, 10.0, 0.1, 'ms')
                        }

    show_params= [        'MolmerSorenson.duration',
                          'MolmerSorenson.line_selection',
                          'MolmerSorenson.frequency_selection',
                          'MolmerSorenson.sideband_selection',
                          'MolmerSorenson.detuning',
                          'MolmerSorenson.ac_stark_shift',
                          'MolmerSorenson.amp_red',
                          'MolmerSorenson.amp_blue'
                          # side band cooling 
                  ]
    
    def run_initial(self):
        gate = self.parameters.MolmerSorensen

        if spc.selection_sideband == "off":         
            freq_729=self.calc_freq(spc.line_selection)
        else:
            freq_729=self.calc_freq(spc.line_selection, spc.selection_sideband ,int(spc.order))
        
        freq_729=freq_729 + spc.carrier_detuning + spc.sideband_detuning

        self.parameters['MolmerSorensen.frequency'] = freq_729
        self.parameters['LocalRotation.frequency'] = freq_729

        mode = gate.sideband_selection
        trap_frequency = self.parameters['TrapFrequencies.' + mode]

        f_global = WithUnit(80.0, 'MHz') + WithUnit(0.15, 'MHz')
        freq_blue = f_global - trap_frequency - gate.detuning + gate.ac_stark_shift
        freq_red = f_global + trap_frequency + gate.detuning  + gate.ac_stark_shift

        amp_blue = self.parameters.MolmerSorensen.amp_blue
        amp_red = self.parameters.MolmerSorensen.amp_red
        self.dds_cw.frequency('0', freq_blue)
        self.dds_cw.frequency('1', freq_red)
        self.dds_cw.frequency('2', f_global) # for driving the carrier
        self.dds_cw.amplitude('0', amp_blue)
        self.dds_cw.amplitude('1', amp_red)

        self.dds_cw.output('0', True)
        self.dds_cw.output('1', True)
        self.dds_cw.output('2', True)
        
        self.dds_cw.output('5', True) # time to thermalize the single pass
        time.sleep(1.0)
        
        self.dds_cw.output('5', False)
        time.sleep(0.5) # just make sure everything is programmed before starting the sequence


    def sequence(self):        
        from StatePreparation import StatePreparation
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
        
        p = self.parameters
        
        self.end = U(10., 'us')
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)     

        if p.MolmerSorensen.SDDS_enable:
        self.addSequence(local_rotation)

        self.addSequence(MolmerSorensen)

        if p.MolmerSorensen.SDDS_rotate_out:
            self.addSequence(local_rotation)
            
        if p.MolmerSorensen.analysis_pulse_enable:
            self.addSequence(global_rotation)

        self.addSequence(StateReadout)






