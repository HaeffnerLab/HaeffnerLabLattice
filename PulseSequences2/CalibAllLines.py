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
    def run_initial(cls,cxn, parameters_dict):
        print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')
        
    @classmethod
    def run_finally(cls, cxn, parameters_dict, all_data, freq_data):
        
        print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)

        # Should find a better way to do this
        global carr_1_global 
        
        # for the multiple case we summ the probabilities, this also
        # reduces the dimension to 1 for single ion case 
        try:
            all_data = all_data.sum(1)
        except ValueError:
            return
        
        #print "139490834", freq_data, all_data
        peak_fit = cls.gaussian_fit(freq_data, all_data)
        print peak_fit
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
    def run_initial(cls,cxn, parameters_dict):
        print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')
        
    @classmethod
    def run_finally(cls, cxn, parameters_dict, all_data, freq_data):
        
        print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)

        
        carrier_translation = {'S+1/2D-3/2':'c0',
                               'S-1/2D-5/2':'c1',
                               'S+1/2D-1/2':'c2',
                               'S-1/2D-3/2':'c3',
                               'S+1/2D+1/2':'c4',
                               'S-1/2D-1/2':'c5',
                               'S+1/2D+3/2':'c6',
                               'S-1/2D+1/2':'c7',
                               'S+1/2D+5/2':'c8',
                               'S-1/2D+3/2':'c9',
                               }
        
        carr_1 = carr_1_global
        
        if not carr_1:
            return
        
          
        # for the multiple case we summ the probabilities, this also
        # reduces the dimension to 1 for single ion case 
        try:
            all_data = all_data.sum(1)
        except ValueError:
            return
            
        peak_fit = cls.gaussian_fit(freq_data, all_data)
        
        if not peak_fit:
            return
        
        peak_fit = U(peak_fit, "MHz") 
          
        carr_2 = peak_fit
        
        line_1 = parameters_dict.DriftTracker.line_selection_1
        line_2 = parameters_dict.DriftTracker.line_selection_2
        #print  "3243"
        #print " peak 1 {}", carr_1 
        #print " peak 2 {}", carr_2
        
        if parameters_dict.Display.relative_frequencies:
            #print "using relative units"
            carr_1 = carr_1+parameters_dict.Carriers[carrier_translation[line_1]]
            carr_2 = carr_2+parameters_dict.Carriers[carrier_translation[line_2]]
        
        
        submission = [(line_1, carr_1), (line_2, carr_2)]
        #print  "3243", submission
              
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
                  'Display.relative_frequencies',
                  'StatePreparation.channel_729',
                  'StatePreparation.optical_pumping_enable',
                  'StatePreparation.sideband_cooling_enable']
                  