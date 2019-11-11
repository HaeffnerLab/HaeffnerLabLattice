import numpy as np
from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict


class CalibAxialCOM(pulse_sequence):
    
    scannable_params = {'Spectrum.carrier_detuning' : [(-10, 10, 0.75, 'kHz'), 'radial1']}


    def sequence(self):

        from StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll

        self.end = U(10., 'us')
        p = self.parameters
        line1 = p.DriftTracker.line_selection_1
        
        freq_729=self.calc_freq(line1, 'axial_frequency' ,int(-1.0))
        freq_729 = freq_729 + p.Spectrum.carrier_detuning
        
        amp = p.Spectrum.manual_amplitude_729
        duration = p.Spectrum.manual_excitation_time
        
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)
        self.addSequence(RabiExcitation,{'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': amp,
                                         'Excitation_729.rabi_excitation_duration':  duration,
                                          })
        self.addSequence(StateReadout)
        
    @classmethod
    def run_initial(cls,cxn, parameters_dict):
        print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')
        
    @classmethod
    def run_finally(cls, cxn, parameters_dict, all_data, freq_data):
        

        
        print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)
        
        print " sequence ident" , int(cxn.scriptscanner.get_running()[0][0])  


class CalibAxialST(pulse_sequence):

    scannable_params = {'Spectrum.carrier_detuning' : [(-10, 10, 0.75, 'kHz'), 'radial2']}


    def sequence(self):

        from StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll

        self.end = U(10., 'us')
        p = self.parameters
        line1 = p.DriftTracker.line_selection_1
        
        freq_729=self.calc_freq(line1, 'aux_axial' ,int(-1.0))
        freq_729 = freq_729 + p.Spectrum.carrier_detuning
        
        amp = p.Spectrum.manual_amplitude_729
        duration = p.Spectrum.manual_excitation_time
        
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)
        self.addSequence(RabiExcitation,{'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': amp,
                                         'Excitation_729.rabi_excitation_duration':  duration })
        self.addSequence(StateReadout)

    @classmethod
    def run_initial(cls,cxn, parameters_dict):
        print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')
        
    @classmethod
    def run_finally(cls, cxn, parameters_dict, all_data, freq_data):
        
        print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)

        
                
class CalibAxialLines(pulse_sequence):
    is_composite = True
    
    sequences = [CalibAxialCOM, CalibAxialST]

    show_params= [
                  'Spectrum.manual_amplitude_729',
                  'Spectrum.manual_excitation_time',
                  'DriftTracker.line_selection_1',
                  'DriftTracker.line_selection_2',
                  'Display.relative_frequencies']
                  