import numpy as np
from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict


class CalibLine1(pulse_sequence):
    
    scannable_params = {'Spectrum.carrier_detuning' : [(-15, 15, 1., 'kHz'), 'car1']}


    def sequence(self):

        from StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll

        self.end = U(10., 'us')
        p = self.parameters
        line1 = p.DriftTracker.line_selection_1
        
        freq_729 = self.calc_freq(line1)
        freq_729 = freq_729 + p.Spectrum.carrier_detuning
        
        amp = p.Spectrum.car2_amp
        duration = p.Spectrum.manual_excitation_time
        
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)
        self.addSequence(RabiExcitation,{'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': amp,
                                         'Excitation_729.rabi_excitation_duration':  duration })
        self.addSequence(StateReadout)
        

    @classmethod
    def run_finally(cls, cxn, parameters_dict, all_data, freq_data):
        
        # Should find a better way to do this
        global carr_1_global 
         
        peak_fit = cls.gaussian_fit(freq_data, all_data)
        
        if not peak_fit:
            carr_1_global = None
            return
        
        peak_fit = U(peak_fit, "MHz") 
        carr_1_global = peak_fit 

class CalibLine2(pulse_sequence):

    scannable_params = {'Spectrum.carrier_detuning' : [(-15, 15, 1., 'kHz'), 'car2']}


    def sequence(self):

        from StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll

        self.end = U(10., 'us')
        p = self.parameters
        line2 = p.DriftTracker.line_selection_2
        
        freq_729 = self.calc_freq(line2)
        freq_729 = freq_729 + p.Spectrum.carrier_detuning
        
        amp = p.Spectrum.car2_amp
        duration = p.Spectrum.manual_excitation_time
        
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)
        self.addSequence(RabiExcitation,{'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': amp,
                                         'Excitation_729.rabi_excitation_duration':  duration })
        self.addSequence(StateReadout)


    @classmethod
    def run_finally(cls, cxn, parameters_dict, all_data, freq_data):
        
        carr_1 = carr_1_global
        
        if not carr_1:
            return
          
        peak_fit = self.gaussian_fit(freq_data, all_data)
        
        if not peak_fit:
            return
        
        peak_fit = U(peak_fit, "MHz") 
          
        carr_2 = peak_fit
        line_1 = self.parameters.DriftTracker.line_selection_1
        line_2 = self.parameters.DriftTracker.line_selection_2
          
        submission = [(line_1, carr_1), (line_2, carr_2)]
          
        cxn.sd_tracker.set_measurements(submission) 
        
class CalibAllLines(pulse_sequence):
    is_composite = True
    
    sequences = [CalibLine1, CalibLine2]

    show_params= ['Excitation_729.channel_729',
                  'Spectrum.car1_amp',
                  'Spectrum.car2_amp',
                  'Spectrum.manual_excitation_time',
                  'DriftTracker.line_selection_1',
                  'DriftTracker.line_selection_2',
                  'Display.relative_frequencies']
                  