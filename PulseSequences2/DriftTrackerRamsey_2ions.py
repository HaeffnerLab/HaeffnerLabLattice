import numpy as np
from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from labrad import units
from treedict import TreeDict
import time
from fractions import Fraction
from common.client_config import client_info as cl


# Should find a better way to do this
detuning_1_global = U(0,'kHz')
auto_schedule = False
        
class TrackLine1(pulse_sequence):
    
    scannable_params = {'DriftTrackerRamsey.phase_1' : [(90, 270, 180, 'deg'), 'current']}
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
        freq_729 = freq_729 + local_detuning_1
                
        amp = p.DriftTrackerRamsey.line_1_amplitude
        duration = p.DriftTrackerRamsey.line_1_pi_time
        ramsey_time = p.DriftTrackerRamsey.gap_time_1
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
        
        ident = int(cxn.scriptscanner.get_running()[-1][0])
        print " sequence ident" , ident

        # for the multiple case we summ the probabilities, this also
        # reduces the dimension to 1 for single ion case 
        all_data = np.array(all_data)
        print all_data
        
        #print "139490834", freq_data, all_data
        
        detuning = None
        
        p = parameters_dict
        duration = p.DriftTrackerRamsey.line_1_pi_time
        ramsey_time = p.DriftTrackerRamsey.gap_time_1
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
            print "Populations are abnormal. Please make sure everything works well."
            print "stoping the sequence ident" , ident                     
            cxn.scriptscanner.stop_sequence(ident)
            return

        global auto_schedule
        auto_schedule = False

        max_gap = U(500, 'us')
        min_gap = U(25, 'us')
        if np.abs((p1-p2)/(p1+p2)) > 0.8:
            new_ramsey_time = ramsey_time/2
            if new_ramsey_time >= min_gap:
                cxn.scriptscanner.set_parameter('DriftTrackerRamsey', 'gap_time_1', new_ramsey_time)
                print "gap_time_1 (line_1) is too big. halve it"
            else:
                cxn.scriptscanner.set_parameter('DriftTrackerRamsey', 'gap_time_1', min_gap)
                print "gap_time_1 (line_1) is too big. Set it to be minimum gaptime: ", min_gap
            if p.DriftTrackerRamsey.auto_schedule:
                cxn.scriptscanner.set_parameter('DriftTrackerRamsey', 'auto_schedule', False)
                scan = [('CalibLine1', ('Spectrum.carrier_detuning', -7, 7, 1.2, 'kHz')), ('CalibLine2', ('Spectrum.carrier_detuning', -7, 7, 1.2, 'kHz'))]
                cxn.scriptscanner.new_sequence('CalibAllLines',scan)
                print "stoping the sequence ident" , ident                     
                cxn.scriptscanner.stop_sequence(ident)
            else:
                auto_schedule = True
                # scan = [('TrackLine1', ('DriftTrackerRamsey.phase_1', 90, 271, 180, 'deg')), ('TrackLine2', ('DriftTrackerRamsey.phase_2', 90, 271, 180, 'deg'))]
                # cxn.scriptscanner.new_sequence('DriftTrackerRamsey_2ions', scan)
                # print "stoping the sequence ident" , ident                     
                # cxn.scriptscanner.stop_sequence(ident)
            return
        elif np.abs((p1-p2)/(p1+p2)) >0.55:
            new_ramsey_time = ramsey_time*2/3
            if new_ramsey_time >= min_gap:
                cxn.scriptscanner.set_parameter('DriftTrackerRamsey', 'gap_time_1', new_ramsey_time)
                print "gap_time_1 (line_1) should be smaller. *2/3"
            else:
                cxn.scriptscanner.set_parameter('DriftTrackerRamsey', 'gap_time_1', min_gap)
                print "gap_time_1 (line_1) should be smaller. Set it to be minimum gaptime: ", min_gap
        elif np.abs((p1-p2)/(p1+p2)) < 0.15:
            new_ramsey_time = ramsey_time*3/2
            if new_ramsey_time < max_gap:
                cxn.scriptscanner.set_parameter('DriftTrackerRamsey', 'gap_time_1', new_ramsey_time)
                print "gap_time_1 (line_1) can be larger. *3/2"
            else:
                cxn.scriptscanner.set_parameter('DriftTrackerRamsey', 'gap_time_1', max_gap)
                print "gap_time_1 (line_1) can be larger. set gap_time_1 to be max gap time: ", max_gap
        
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

    scannable_params = {'DriftTrackerRamsey.phase_2' : [(90, 270, 180, 'deg'), 'current']}
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
        freq_729 = freq_729 + local_detuning_2
                
        amp = p.DriftTrackerRamsey.line_2_amplitude
        duration = p.DriftTrackerRamsey.line_2_pi_time
        ramsey_time = p.DriftTrackerRamsey.gap_time_2
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
        
        ident = int(cxn.scriptscanner.get_running()[-1][0])
        print " sequence ident" , ident

        # Should find a better way to do this
        #global detuning_1_global 
        
        # for the multiple case we summ the probabilities, this also
        # reduces the dimension to 1 for single ion case 
        all_data = np.array(all_data)
        print all_data
                        
        p = parameters_dict
        duration = p.DriftTrackerRamsey.line_2_pi_time
        ramsey_time = p.DriftTrackerRamsey.gap_time_2
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
            print "Populations are abnormal. Please make sure everything works well."
            # print "stoping the sequence ident" , ident                     
            # cxn.scriptscanner.stop_sequence(ident)
            return

        max_gap = U(500, 'us')
        min_gap = U(25, 'us')
        if np.abs((p1-p2)/(p1+p2)) > 0.8:
            new_ramsey_time = ramsey_time/2
            if new_ramsey_time >= min_gap:
                cxn.scriptscanner.set_parameter('DriftTrackerRamsey', 'gap_time_2', new_ramsey_time)
                print "gap_time_2 (line_2) is too big. halve it"
            else:
                cxn.scriptscanner.set_parameter('DriftTrackerRamsey', 'gap_time_2', min_gap)
                print "gap_time_2 (line_2) is too big. Set it to be minimum gaptime: ", min_gap
            if p.DriftTrackerRamsey.auto_schedule:
                cxn.scriptscanner.set_parameter('DriftTrackerRamsey', 'auto_schedule', False)
                scan = [('CalibLine1', ('Spectrum.carrier_detuning', -7, 7, 1.2, 'kHz')), ('CalibLine2', ('Spectrum.carrier_detuning', -7, 7, 1.2, 'kHz'))]
                cxn.scriptscanner.new_sequence('CalibAllLines',scan)
                # print "stoping the sequence ident" , ident                     
                # cxn.scriptscanner.stop_sequence(ident)
            else:
                cxn.scriptscanner.set_parameter('DriftTrackerRamsey', 'auto_schedule', True)
                scan = [('TrackLine1', ('DriftTrackerRamsey.phase_1', 90, 270, 180, 'deg')), ('TrackLine2', ('DriftTrackerRamsey.phase_2', 90, 270, 180, 'deg'))]
                cxn.scriptscanner.new_sequence('DriftTrackerRamsey_2ions', scan)
                # print "stoping the sequence ident" , ident                     
                # cxn.scriptscanner.stop_sequence(ident)
            return
        elif np.abs((p1-p2)/(p1+p2)) >0.55:
            new_ramsey_time = ramsey_time*2/3
            if new_ramsey_time >= min_gap:
                cxn.scriptscanner.set_parameter('DriftTrackerRamsey', 'gap_time_2', new_ramsey_time)
                print "gap_time_2 (line_2) should be smaller. *2/3"
            else:
                cxn.scriptscanner.set_parameter('DriftTrackerRamsey', 'gap_time_2', min_gap)
                print "gap_time_2 (line_2) should be smaller. Set it to be minimum gaptime: ", min_gap
        elif np.abs((p1-p2)/(p1+p2)) < 0.15:
            new_ramsey_time = ramsey_time*3/2
            if new_ramsey_time < max_gap:
                cxn.scriptscanner.set_parameter('DriftTrackerRamsey', 'gap_time_2', new_ramsey_time)
                print "gap_time_2 (line_2) can be larger. *3/2"
            else:
                cxn.scriptscanner.set_parameter('DriftTrackerRamsey', 'gap_time_2', max_gap)
                print "gap_time_2 (line_2) can be larger. set gap_time_2 to be max gap time: ", max_gap

        if auto_schedule:
            cxn.scriptscanner.set_parameter('DriftTrackerRamsey', 'auto_schedule', True)
            scan = [('TrackLine1', ('DriftTrackerRamsey.phase_1', 90, 270, 180, 'deg')), ('TrackLine2', ('DriftTrackerRamsey.phase_2', 90, 270, 180, 'deg'))]
            cxn.scriptscanner.new_sequence('DriftTrackerRamsey_2ions', scan)
            return
        else:
            cxn.scriptscanner.set_parameter('DriftTrackerRamsey', 'auto_schedule', False)
        
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
            import labrad
            global_sd_cxn = labrad.connect(cl.global_address, password = cl.global_password,tls_mode='off')
            print cl.client_name , "is sub lines to global SD" , 
            print submission 
            global_sd_cxn.sd_tracker_global.set_measurements(submission,cl.client_name) 
            global_sd_cxn.disconnect()
        
        
class DriftTrackerRamsey_2ions(pulse_sequence):
    is_composite = True
    # at the moment fixed params are shared between the sub sequence!!! 
    fixed_params = {'StatePreparation.aux_optical_pumping_enable': False,
                    'StatePreparation.sideband_cooling_enable': True,
                    'StateReadout.readout_mode':'camera',
                    'Excitation_729.channel_729': "729global",
                    'StatePreparation.channel_729': "729global",
                    'SidebandCooling.selection_sideband': "axial_frequency",
                    'CalibrationScans.calibration_channel_729': "729global"
                    }
    
    sequence = [TrackLine1, TrackLine2]

    show_params= ['DriftTrackerRamsey.line_1_amplitude',
                  'DriftTrackerRamsey.line_1_pi_time',
                  'DriftTrackerRamsey.line_2_amplitude',
                  'DriftTrackerRamsey.line_2_pi_time',
                  'DriftTracker.line_selection_1',
                  'DriftTracker.line_selection_2',
                  'DriftTrackerRamsey.gap_time_1',
                  'DriftTrackerRamsey.gap_time_2',
                  'DriftTrackerRamsey.submit',
                  'DriftTrackerRamsey.bfield_difference_2ions',
                  'DriftTrackerRamsey.no_of_readout_ion_2ions',
                  # 'DriftTrackerRamsey.auto_calibrate_pitime',
                  'DriftTrackerRamsey.first_run',
                  ]

    @classmethod
    def run_initial(cls,cxn, parameters_dict):
        ident = int(cxn.scriptscanner.get_running()[-1][0])
        print " sequence ident" , ident
        
        p = parameters_dict

        if p.DriftTrackerRamsey.first_run:
            scan1 = [('CalibLine1', ('Spectrum.carrier_detuning', -5, 5, 0.75, 'kHz')), ('CalibLine2', ('Spectrum.carrier_detuning', -5, 5, 0.75, 'kHz'))]
            cxn.scriptscanner.new_sequence('CalibAllLines',scan1)

            scan2 = [('RabiLine1', ('RabiFlopping.duration', 0., 15., 3., 'us')), ('RabiLine2', ('RabiFlopping.duration', 0., 15., 3., 'us'))]
            cxn.scriptscanner.new_sequence('DTRamseyCalibPitime', scan2)

            cxn.scriptscanner.set_parameter('DriftTrackerRamsey', 'first_run', False)

            scan3 = [('TrackLine1', ('DriftTrackerRamsey.phase_1', 90, 270, 180, 'deg')), ('TrackLine2', ('DriftTrackerRamsey.phase_2', 90, 270, 180, 'deg'))]
            cxn.scriptscanner.new_sequence('DriftTrackerRamsey_2ions', scan3)

            print "stoping the sequence ident" , ident
            cxn.scriptscanner.stop_sequence(ident)
