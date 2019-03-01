import numpy as np
from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
from common.client_config import client_info as cl
from time import sleep

class CalibLine1(pulse_sequence):
    
    scannable_params = {'Spectrum.carrier_detuning' : [(-5, 5, .75, 'kHz'), 'car1']}
    # fixed parmas doesn't work -> you can declare fixed params for all the seq at the main class

    show_params= ['CalibrationScans.calibration_channel_729',
                  'Spectrum.car1_amp',
                  'Spectrum.car2_amp',
                  'Spectrum.manual_excitation_time',
                  'DriftTracker.line_selection_1',
                  'DriftTracker.line_selection_2',
                  'Display.relative_frequencies',
                  'CalibrationScans.readout_mode']

    fixed_params = {'opticalPumping.line_selection': 'S-1/2D+3/2',
                    'Display.relative_frequencies': False,
                    'StatePreparation.aux_optical_pumping_enable': False,
                    # 'StatePreparation.sideband_cooling_enable': False,
                    'StateReadout.readout_mode': "pmt"}

    def sequence(self):

        from StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll

        self.end = U(10., 'us')
        
        p = self.parameters
        line1 = p.DriftTracker.line_selection_1
        
        # Should find better way to do this
        
        freq_729 = self.calc_freq(line1)
        freq_729 = freq_729 + p.Spectrum.carrier_detuning
        
        amp = p.Spectrum.car1_amp
        duration = p.Spectrum.manual_excitation_time
        channel_729= p.CalibrationScans.calibration_channel_729
        
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)
        self.addSequence(RabiExcitation,{'Excitation_729.channel_729': channel_729,
                                         'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': amp,
                                         'Excitation_729.rabi_excitation_duration':  duration })
        
        self.addSequence(StateReadout)
        
    @classmethod
    def run_initial(cls,cxn, parameters_dict):
#        print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')
        
    @classmethod
    def run_finally(cls, cxn, parameters_dict, all_data, freq_data):
        

        
#        print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)

        return 0.8

class CalibLine2(pulse_sequence):

    scannable_params = {'Spectrum.carrier_detuning' : [(-5, 5, .75, 'kHz'), 'car2']}
    # fixed parmas doesn't work -> you can declare fixed params for all the seq at the main class

    show_params= ['CalibrationScans.calibration_channel_729',
                  'Spectrum.car1_amp',
                  'Spectrum.car2_amp',
                  'Spectrum.manual_excitation_time',
                  'DriftTracker.line_selection_1',
                  'DriftTracker.line_selection_2',
                  'Display.relative_frequencies',
                  'CalibrationScans.readout_mode']

    fixed_params = {'opticalPumping.line_selection': 'S-1/2D+3/2',
                    'Display.relative_frequencies': False,
                    'StatePreparation.aux_optical_pumping_enable': False,
                    # 'StatePreparation.sideband_cooling_enable': False,
                    'StateReadout.readout_mode': "pmt"}

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
        channel_729= p.CalibrationScans.calibration_channel_729
        
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)
        self.addSequence(RabiExcitation,{'Excitation_729.channel_729': channel_729,
                                         'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': amp,
                                         'Excitation_729.rabi_excitation_duration':  duration })
        
        self.addSequence(StateReadout)
        
    @classmethod
    def run_initial(cls,cxn, parameters_dict):
#        print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')
        
    @classmethod
    def run_finally(cls, cxn, parameters_dict, all_data, freq_data):
        
#        print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)
        

        return 0.2
        
class multi_test(pulse_sequence):

    is_2dimensional = True
    is_composite = True

    # sequence = [CalibLine1, CalibLine2] 
    sequence = [(CalibLine1, {'StateReadout.readout_mode': 'CalibrationScans.readout_mode'}), 
                 (CalibLine2, {'StateReadout.readout_mode': 'CalibrationScans.readout_mode'})]

    @classmethod
    def run_finally(cls, cxn, parameters_dict, all_data, freq_data):
        
#        print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)
        sleep(0.5)

        return 0.5



                  
