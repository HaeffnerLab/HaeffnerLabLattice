import numpy as np
from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import time
        
class DriftTrackerRamsey_test(pulse_sequence):
    # at the moment fixed params are shared between the sub sequence!!! 
    fixed_params = {'StatePreparation.aux_optical_pumping_enable': False,
                    'StatePreparation.sideband_cooling_enable': False,
                    'StateReadout.readout_mode':'pmt',
                    'Excitation_729.channel_729': "729global",
                    
                    
                    }

    scannable_params = {'DriftTrackerRamsey.phase_1' : [(90, 271, 180, 'deg'), 'current']}

    show_params= ['CalibrationScans.calibration_channel_729',
                  'DriftTrackerRamsey.line_1_amplitude',
                  'DriftTrackerRamsey.line_1_pi_time',
                  'DriftTrackerRamsey.line_2_amplitude',
                  'DriftTrackerRamsey.line_2_pi_time',
                  'DriftTracker.line_selection_1',
                  'DriftTracker.line_selection_2',
                  'DriftTrackerRamsey.gap_time',
                  'DriftTrackerRamsey.submit',
                  ]

    def sequence(self):
        
        from StatePreparation import StatePreparation
        from subsequences.GlobalRotation import GlobalRotation
        from subsequences.StateReadout import StateReadout
        from subsequences.EmptySequence import EmptySequence
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
        from subsequences.RabiExcitation import RabiExcitation

        self.end = U(10., 'us')
        p = self.parameters
        line1 = p.DriftTracker.line_selection_1
        line2 = p.DriftTracker.line_selection_2
        
        channel_729= p.CalibrationScans.calibration_channel_729
        freq_729_1 = self.calc_freq(line1)
        detuning = p.DriftTrackerRamsey.detuning
        freq_729_1 =freq_729_1 + detuning
        freq_729_2 = self.calc_freq(line2)
        detuning = p.DriftTrackerRamsey.detuning
        freq_729_2 =freq_729_2 + detuning
                
        amp_1 = p.DriftTrackerRamsey.line_1_amplitude
        duration_1 = p.DriftTrackerRamsey.line_1_pi_time
        amp_2 = p.DriftTrackerRamsey.line_2_amplitude
        duration_2 = p.DriftTrackerRamsey.line_2_pi_time
        ramsey_time = p.DriftTrackerRamsey.gap_time
        phase_2nd_pulse=p.DriftTrackerRamsey.phase_1
        
        print "RAMSEY PARAMS"
        print freq_729_1, freq_729_2
        print amp_1, amp_2
        print duration_1, duration_2
        print ramsey_time
        print phase_2nd_pulse
        
        
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)
        self.addSequence(RabiExcitation,{'Excitation_729.channel_729': channel_729,
                                         'Excitation_729.rabi_excitation_frequency': freq_729_1,
                                         'Excitation_729.rabi_excitation_amplitude': amp_1,
                                         'Excitation_729.rabi_excitation_duration':  0.5*duration_1,
                                         'Excitation_729.rabi_excitation_phase': U(0, 'deg')
                                          })
        # self.addSequence(GlobalRotation, { "GlobalRotation.frequency":freq_729_1,
        #                                    "GlobalRotation.angle": U(np.pi/2.0, 'rad'),
        #                                    "GlobalRotation.phase": U(0, 'deg'),
        #                                    "GlobalRotation.amplitude": amp_1})
    
        
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : ramsey_time})
        
        self.addSequence(RabiExcitation,{'Excitation_729.channel_729': channel_729,
                                         'Excitation_729.rabi_excitation_frequency': freq_729_1,
                                         'Excitation_729.rabi_excitation_amplitude': amp_1,
                                         'Excitation_729.rabi_excitation_duration':  0.5*duration_1,
                                         'Excitation_729.rabi_excitation_phase': phase_2nd_pulse
                                          })
        # self.addSequence(GlobalRotation, {"GlobalRotation.frequency":freq_729_1, 
        #                                   "GlobalRotation.angle": U(np.pi/2.0, 'rad'), 
        #                                   "GlobalRotation.phase": phase_2nd_pulse,
        #                                   "GlobalRotation.amplitude": amp})
        self.addSequence(StateReadout)

        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)
        self.addSequence(RabiExcitation,{'Excitation_729.channel_729': channel_729,
                                         'Excitation_729.rabi_excitation_frequency': freq_729_2,
                                         'Excitation_729.rabi_excitation_amplitude': amp_2,
                                         'Excitation_729.rabi_excitation_duration':  0.5*duration_2,
                                         'Excitation_729.rabi_excitation_phase': U(0, 'deg')
                                          })
        # self.addSequence(GlobalRotation, { "GlobalRotation.frequency":freq_729_1,
        #                                    "GlobalRotation.angle": U(np.pi/2.0, 'rad'),
        #                                    "GlobalRotation.phase": U(0, 'deg'),
        #                                    "GlobalRotation.amplitude": amp_1})
    
        
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : ramsey_time})
        
        self.addSequence(RabiExcitation,{'Excitation_729.channel_729': channel_729,
                                         'Excitation_729.rabi_excitation_frequency': freq_729_2,
                                         'Excitation_729.rabi_excitation_amplitude': amp_2,
                                         'Excitation_729.rabi_excitation_duration':  0.5*duration_2,
                                         'Excitation_729.rabi_excitation_phase': phase_2nd_pulse
                                          })
        # self.addSequence(GlobalRotation, {"GlobalRotation.frequency":freq_729_1, 
        #                                   "GlobalRotation.angle": U(np.pi/2.0, 'rad'), 
        #                                   "GlobalRotation.phase": phase_2nd_pulse,
        #                                   "GlobalRotation.amplitude": amp})
        self.addSequence(StateReadout)

    @classmethod
    def run_initial(cls,cxn, parameters_dict):
        print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')
        
    @classmethod
    def run_finally(cls, cxn, parameters_dict, all_data, Phase):
        
        print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)
        
        print " sequence ident" , int(cxn.scriptscanner.get_running()[0][0])

        all_data = np.array(all_data)
        try:
            all_data = all_data.sum(1)
        except ValueError:
            return
                        
        p = parameters_dict
        duration_1 = p.DriftTrackerRamsey.line_1_pi_time
        duration_2 = p.DriftTrackerRamsey.line_2_pi_time
        ramsey_time = p.DriftTrackerRamsey.gap_time

        p11 =all_data[0]
        p12 =all_data[2]
        p21 =all_data[1]
        p22 =all_data[3]

        detuning_1 = 1.0*np.arcsin((p11-p12)/(p11+p12))/(2.0*np.pi*ramsey_time['s'] + 4*duration_1['s'])/1000.0
        detuning_1 = U(detuning_1, "kHz")
        detuning_2 = 1.0*np.arcsin((p21-p22)/(p21+p22))/(2.0*np.pi*ramsey_time['s'] + 4*duration_2['s'])/1000.0
        detuning_2 = U(detuning_2, "kHz")

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
        line_1 = parameters_dict.DriftTracker.line_selection_1
        line_2 = parameters_dict.DriftTracker.line_selection_2

        carr_1 = detuning_1+parameters_dict.Carriers[carrier_translation[line_1]]
        carr_2 = detuning_2+parameters_dict.Carriers[carrier_translation[line_2]]

        print "DFIRT TRACKER FINAL"
        print "Ramsey max frequency shift" , 1/(4*ramsey_time['s'] + 8*duration['s']/np.pi)*1e-3 ,'kHz'
        print " calculated detuning_1",detuning_1, " and the carrier", line_1, "freq",carr_1
        print " calculated detuning_2",detuning_2," and the carrier", line_2, "freq",carr_2
        
        submission = [(line_1, carr_1), (line_2, carr_2)]
        print  "3243", submission
        
        if parameters_dict.DriftTrackerRamsey.submit:   
            print " submitting to df server"   
            cxn.sd_tracker.set_measurements(submission) 