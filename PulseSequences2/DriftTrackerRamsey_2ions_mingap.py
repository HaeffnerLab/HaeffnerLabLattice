import numpy as np
from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from labrad import units
from treedict import TreeDict
import time
from fractions import Fraction


# Should find a better way to do this
detuning_1_global = U(0,'kHz')
gap_time_1 = U(80, 'us')
gap_time_2 = U(30, 'us') 
        
class TrackLine1(pulse_sequence):
    
    scannable_params = {'DriftTrackerRamsey.phase_1' : [(90, 271, 180, 'deg'), 'current']}
    # fixed parmas doesn't work -> you can declare fixed params for all the seq at the main class
#     fixed_params = {'StateReadout.readout_mode':'pmt'}

    def sequence(self):

        from StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.EmptySequence import EmptySequence
        from subsequences.TurnOffAll import TurnOffAll
        from subsequences.GlobalRotation import GlobalRotation

        self.end = U(10., 'us')
        p = self.parameters
        line1 = p.DriftTracker.line_selection_1
        
        b_dif = p.DriftTrackerRamsey.bfield_difference_2ions
        ion_no = p.DriftTrackerRamsey.no_of_readout_ion_2ions
        ms = Fraction(line1[1:5])
        md = Fraction(line1[6:10])
        g_factor_S = 2.00225664
        g_factor_D = 1.2003340
        energy_scale = units.bohr_magneton / units.hplanck #1.4 MHz / gauss
        local_detuning_1 = (ion_no - 3/2) * b_dif * (g_factor_D * md - g_factor_S * ms) * energy_scale

        print line1
        print ms
        print md
        print energy_scale

        channel_729= p.CalibrationScans.calibration_channel_729
        freq_729 = self.calc_freq(line1)
        detuning = p.DriftTrackerRamsey.detuning
        freq_729 =freq_729 +detuning
        freq_729 = freq_729 + local_detuning_1
                
        amp = p.DriftTrackerRamsey.line_1_amplitude
        duration = p.DriftTrackerRamsey.line_1_pi_time
        ramsey_time = gap_time_1
        phase_2nd_pulse=p.DriftTrackerRamsey.phase_1
        
        print "RAMSEY PARAMS"
        print freq_729
        print amp
        print duration
        print ramsey_time
        print phase_2nd_pulse
        
        
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)
        self.addSequence(RabiExcitation,{'Excitation_729.channel_729': channel_729,
                                         'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': amp,
                                         'Excitation_729.rabi_excitation_duration':  0.5*duration,
                                         'Excitation_729.rabi_excitation_phase': U(0, 'deg')
                                          })
        # self.addSequence(GlobalRotation, { "GlobalRotation.frequency":freq_729,
        #                                    "GlobalRotation.angle": U(np.pi/2.0, 'rad'),
        #                                    "GlobalRotation.phase": U(0, 'deg'),
        #                                    "GlobalRotation.amplitude": amp})
    
        
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : ramsey_time})
        
        self.addSequence(RabiExcitation,{'Excitation_729.channel_729': channel_729,
                                         'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': amp,
                                         'Excitation_729.rabi_excitation_duration':  0.5*duration,
                                         'Excitation_729.rabi_excitation_phase': phase_2nd_pulse
                                          })
        # self.addSequence(GlobalRotation, {"GlobalRotation.frequency":freq_729, 
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
        
        print " sequence ident" , int(cxn.scriptscanner.get_running()[-1][0])  

        
        # for the multiple case we summ the probabilities, this also
        # reduces the dimension to 1 for single ion case 
        all_data = np.array(all_data)
        print all_data
        
        #print "139490834", freq_data, all_data
        
        detuning = None
        
        p = parameters_dict
        duration = p.DriftTrackerRamsey.line_1_pi_time
        ramsey_time = gap_time_1
        ion_no = p.DriftTrackerRamsey.no_of_readout_ion_2ions
        
        ind1 = np.where(Phase == 90.0)
        ind2 = np.where(Phase == 270.0)
        
        try:
            p1 =all_data[ind1][0][ion_no - 1]
            p2 =all_data[ind2][0][ion_no - 1]
        except:
            print "cannot get population p1 & p2"
            return
        
        if p1 == p2 == 0.0 or p1 == p2 == 1.0:
            print "Populations are zero. Please make sure everything works well."
            return
        
        if np.abs((p1-p2)/(p1+p2)) > 0.8:
            scan = [('CalibLine1', ('Spectrum.carrier_detuning', -5, 5, .75, 'kHz')), ('CalibLine2', ('Spectrum.carrier_detuning', -5, 5, .75, 'kHz'))]
            cxn.scriptscanner.new_sequence('CalibAllLines',scan)
            print "stoping the sequence ident" , ident                     
            cxn.scriptscanner.stop_sequence(ident)
            return

        detuning = 1.0*np.arcsin((p1-p2)/(p1+p2))/(2.0*np.pi*ramsey_time['s'] + 4*duration['s'])/1000.0
        
        
        
#         if not detuning:
#             detuning_1_global = None
#             print "4321"
#             ident = int(cxn.scriptscanner.get_running()[0][0])
#             print "stoping the sequence ident" , ident                     
#             cxn.scriptscanner.stop_sequence(ident)
#             return
        print "at ",Phase[ind1], " the pop is", p1  
        print "at ",Phase[ind2], " the pop is", p2
        print "Ramsey time", ramsey_time," and the calculated detuning", detuning, "in kHz"
        
        # # if we don't lost the ion or we don't have good readout than the detuning would be zero in this case we don't want to proccesd 
        # if detuning == 0.0:
            
        #     print "4321"
        #     ident = int(cxn.scriptscanner.get_running()[0][0])
        #     print "stoping the sequence ident" , ident                     
        #     cxn.scriptscanner.stop_sequence(ident)
        #     return
        
        detuning = detuning.mean()
        detuning = U(detuning, "kHz")
        global detuning_1_global 
        detuning_1_global = detuning 
        
        

class TrackLine2(pulse_sequence):

    scannable_params = {'DriftTrackerRamsey.phase_2' : [(90, 271, 180, 'deg'), 'current']}
    # fixed parmas doesn't work -> you can declare fixed params for all the seq at the main class
    #fixed_params = {'StateReadout.readout_mode':'pmt'}

    def sequence(self):

        from StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.EmptySequence import EmptySequence
        from subsequences.TurnOffAll import TurnOffAll
        from subsequences.GlobalRotation import GlobalRotation      
  

        self.end = U(10., 'us')
        p = self.parameters
        line2 = p.DriftTracker.line_selection_2

        b_dif = p.DriftTrackerRamsey.bfield_difference_2ions
        ion_no = p.DriftTrackerRamsey.no_of_readout_ion_2ions
        ms = Fraction(line2[1:5])
        md = Fraction(line2[6:10])
        g_factor_S = 2.00225664
        g_factor_D = 1.2003340
        energy_scale = units.bohr_magneton / units.hplanck #1.4 MHz / gauss
        local_detuning_2 = (ion_no - 3/2) * b_dif * (g_factor_D * md - g_factor_S * ms) * energy_scale
        
        print line2
        print ms
        print md
        print energy_scale

        channel_729= p.CalibrationScans.calibration_channel_729
        freq_729 = self.calc_freq(line2)
        detuning = p.DriftTrackerRamsey.detuning
        freq_729 =freq_729 +detuning
        freq_729 = freq_729 + local_detuning_2
                
        amp = p.DriftTrackerRamsey.line_2_amplitude
        duration = p.DriftTrackerRamsey.line_2_pi_time
        ramsey_time = gap_time_2
        phase_2nd_pulse=p.DriftTrackerRamsey.phase_2
        
        print "RAMSEY PARAMS"
        print freq_729
        print amp
        print duration
        print ramsey_time
        print phase_2nd_pulse
        
        
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)
        self.addSequence(RabiExcitation,{'Excitation_729.channel_729': channel_729,
                                         'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': amp,
                                         'Excitation_729.rabi_excitation_duration':  0.5*duration,
                                         'Excitation_729.rabi_excitation_phase': U(0, 'deg')
                                          })
  
        # self.addSequence(GlobalRotation, { "GlobalRotation.frequency":freq_729,
        #                                    "GlobalRotation.angle": U(np.pi/2.0, 'rad'),
        #                                    "GlobalRotation.phase": U(0, 'deg'),
        #                                    "GlobalRotation.amplitude": amp})
        
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : ramsey_time})
        
        self.addSequence(RabiExcitation,{'Excitation_729.channel_729': channel_729,
                                         'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': amp,
                                         'Excitation_729.rabi_excitation_duration':  0.5*duration,
                                         'Excitation_729.rabi_excitation_phase': phase_2nd_pulse
                                          })
        
        # self.addSequence(GlobalRotation, {"GlobalRotation.frequency":freq_729, 
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
        
        print " sequence ident" , int(cxn.scriptscanner.get_running()[-1][0])  

        # Should find a better way to do this
        #global detuning_1_global 
        
        # for the multiple case we summ the probabilities, this also
        # reduces the dimension to 1 for single ion case 
        all_data = np.array(all_data)
        print all_data
                        
        p = parameters_dict
        duration = p.DriftTrackerRamsey.line_1_pi_time
        ramsey_time = gap_time_2
        ion_no = p.DriftTrackerRamsey.no_of_readout_ion_2ions
        
        ind1 = np.where(Phase == 90.0)
        ind2 = np.where(Phase == 270.0)
        
        try:
            p1 =all_data[ind1][0][ion_no - 1]
            p2 =all_data[ind2][0][ion_no - 1]
        except:
            print "cannot get population p1 & p2"
            return

        if p1 == p2 == 0.0 or p1 == p2 == 1.0:
            print "Populations are zero. Please make sure everything works well."
            return
        
        if np.abs((p1-p2)/(p1+p2)) > 0.8:
            scan = [('CalibLine1', ('Spectrum.carrier_detuning', -5, 5, .75, 'kHz')), ('CalibLine2', ('Spectrum.carrier_detuning', -5, 5, .75, 'kHz'))]
            cxn.scriptscanner.new_sequence('CalibAllLines',scan)
            # print "stoping the sequence ident" , ident                     
            # cxn.scriptscanner.stop_sequence(ident)
            return

        detuning_2 = 1.0*np.arcsin((p1-p2)/(p1+p2))/(2.0*np.pi*ramsey_time['s'] + 4*duration['s'])/1000.0
        detuning_2 = detuning_2.mean()
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
        
        global detuning_1_global 
        
        
        carr_1 = detuning_1_global+parameters_dict.Carriers[carrier_translation[line_1]]
        carr_2 = detuning_2+parameters_dict.Carriers[carrier_translation[line_2]]
        
        print "DFIRT TRACKER FINAL"
        print "Ramsey max frequency shift" , 1/(4*ramsey_time['s'] + 8*duration['s']/np.pi)*1e-3 ,'kHz'
        print " calculated detuning_1",detuning_1_global, " and the carrier", line_1, "freq",carr_1
        print " calculated detuning_2",detuning_2," and the carrier", line_2, "freq",carr_2
        
        submission = [(line_1, carr_1), (line_2, carr_2)]
        print  "3243", submission
        localtime = time.localtime()
        timetag = time.strftime('%H%M_%S', localtime)
        print timetag
        print carr_1
        print carr_2
        
        # temp=  np.zeros(1, dtype=[('timetag', 'U7'), ('car1', float),('car2', float)])
#         temp['timetag']=timetag
#         temp['car1']=carr_1['kHz']
#         temp['car2']=carr_2['kHz']
#        saving the data to check for the accuracy of this measurement
        # f_handle = file('Drift_tracker.csv','a')
        # np.savetxt(f_handle,temp, fmt="%10s %10.3f %10.3f")
        # f_handle.close()
        
        #np.savetxt('Dfirt_tracker.csv', (timetag,carr_1,carr_2),  delimiter=',', fmt="%7s %10.3f %10.3f")
        
        if parameters_dict.DriftTrackerRamsey.submit:   
            print " submitting to df server"   
            cxn.sd_tracker.set_measurements(submission) 
        
        
class DriftTrackerRamsey_2ions_mingap(pulse_sequence):
    is_composite = True
    # at the moment fixed params are shared between the sub sequence!!! 
    fixed_params = {'StatePreparation.aux_optical_pumping_enable': False,
                    'StatePreparation.sideband_cooling_enable': True,
                    'StateReadout.readout_mode':'camera',
                    'Excitation_729.channel_729': "729global",
                    
                    
                    }
    
    sequences = [TrackLine1, TrackLine2]

    show_params= ['CalibrationScans.calibration_channel_729',
                  'DriftTrackerRamsey.line_1_amplitude',
                  'DriftTrackerRamsey.line_1_pi_time',
                  'DriftTrackerRamsey.line_2_amplitude',
                  'DriftTrackerRamsey.line_2_pi_time',
                  'DriftTracker.line_selection_1',
                  'DriftTracker.line_selection_2',
                  'DriftTrackerRamsey.submit',
                  'DriftTrackerRamsey.bfield_difference_2ions',
                  'DriftTrackerRamsey.no_of_readout_ion_2ions',
                  ]
                  