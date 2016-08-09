class config(object):

    #list in the format (import_path, class_name)
    scripts = [
               #('lattice.scripts.experiments.FFT.fft_spectrum', 'fft_spectrum'), 
               #('lattice.scripts.experiments.Experiments729.Ramsey_with_Heating', 'ramsey_with_heating'), 
               #('lattice.scripts.experiments.Experiments729.Ramsey_with_Heating_and_Cryst', 'ramsey_with_heating_and_cryst'), 
               #('lattice.scripts.experiments.Experiments729.Ramsey_with_Heating_and_Cryst_Scan_Blue', 'ramsey_with_heating_and_cryst_scan_blue'),
               #('lattice.scripts.experiments.Experiments729.Ramsey_with_Heating_and_Cryst_Scan_Both', 'ramsey_with_heating_and_cryst_scan_both'),
#                ('lattice.scripts.experiments.FFT.fft_peak_area', 'fft_peak_area'), 
#                ('lattice.scripts.experiments.FFT.fft_hv_scan', 'fft_hv_scan'), 
#                ('lattice.scripts.experiments.Misc.set_high_volt', 'set_high_volt'), 
               #('lattice.scripts.experiments.Misc.set_linetrigger_offset', 'set_linetrigger_offset'), 
               #('lattice.scripts.experiments.CavityScan.scan_cavity', 'scan_cavity'), 
               #('lattice.scripts.experiments.CavityScan.scan_cavity_397', 'scan_cavity_397'), 
               #('lattice.scripts.experiments.CavityScan.scan_cavity_866', 'scan_cavity_866'), 
#                ('lattice.scripts.experiments.Experiments729.excitation_729', 'excitation_729'), 
               ('lattice.scripts.experiments.Experiments729.spectrum', 'spectrum'), 
               ('lattice.scripts.experiments.Experiments729.rabi_flopping', 'rabi_flopping'), 
#                ('lattice.scripts.experiments.Experiments729.drift_tracker', 'drift_tracker'), 
#                ('lattice.scripts.experiments.Experiments729.excitation_ramsey', 'excitation_ramsey'), 
               ('lattice.scripts.experiments.Experiments729.ramsey_scangap', 'ramsey_scangap'), 
               ('lattice.scripts.experiments.Experiments729.ramsey_scanphase', 'ramsey_scanphase'), 
#                ('lattice.scripts.experiments.Experiments729.excitation_rabi_tomography', 'excitation_rabi_tomography'), 
               #('lattice.scripts.experiments.Experiments729.rabi_tomography', 'rabi_tomography'), 
               #('lattice.scripts.experiments.BareLineScan.BareLineScanRed', 'bare_line_scan_red'), 
               #('lattice.scripts.experiments.BareLineScan.BareLineScan', 'bare_line_scan'),
               #('lattice.scripts.experiments.AO_calibration.AO_calibration', 'AO_calibration'), 
               ('lattice.scripts.experiments.Experiments729.drift_tracker_ramsey', 'drift_tracker_ramsey'), 
               ('lattice.scripts.experiments.Camera.reference_image', 'reference_camera_image'), 
               ('lattice.scripts.experiments.Camera.ion_auto_load', 'ion_auto_load'), 
               #('lattice.scripts.experiments.Lifetime_P.lifetime_p', 'lifetime_p'), 
               ('lattice.scripts.experiments.Experiments729.rabi_flop_scannable', 'rabi_flopping_scannable'), 
               #('lattice.scripts.experiments.Experiments729.ramsey_2ions_scangap_parity', 'ramsey_2ions_scangap_parity'),
               #('lattice.scripts.experiments.Experiments729.rabi_flopping_2ions', 'rabi_flopping_2ions'),
               #('lattice.scripts.experiments.Experiments729.Parity_LLI_scan_gap', 'Parity_LLI_scan_gap'),
               #('lattice.scripts.experiments.Experiments729.Parity_LLI_scan_phase', 'Parity_LLI_scan_phase'),
               ('lattice.scripts.experiments.Experiments729.Sideband_tracker', 'Sideband_tracker'),
               #('lattice.scripts.experiments.Experiments729.Parity_LLI_phase_tracker', 'Parity_LLI_phase_tracker'),
               #('lattice.scripts.experiments.Experiments729.Parity_LLI_monitor', 'Parity_LLI_monitor'),
               #('lattice.scripts.experiments.Experiments729.Parity_LLI_2_point_monitor', 'Parity_LLI_2_point_monitor'),
               #('lattice.scripts.experiments.Experiments729.rabi_power_flopping_2ions', 'Rabi_power_flopping_2ions'),
               #('lattice.scripts.experiments.Experiments729.Parity_LLI_rabi_power_fitter', 'Parity_LLI_rabi_power_fitter'),
#                ('lattice.scripts.experiments.Experiments729.blue_heat_rabi_flopping', 'blue_heat_rabi_flopping'), 
#                ('lattice.scripts.experiments.Experiments729.blue_heat_spectrum', 'blue_heat_spectrum'), 
#                ('lattice.scripts.experiments.Experiments729.blue_heat_scan_delay', 'blue_heat_scan_delay'), 
#                ('lattice.scripts.experiments.Experiments729.blue_heat_scan_pulse_freq', 'blue_heat_scan_pulse_freq'), 
#                ('lattice.scripts.experiments.Experiments729.blue_heat_scan_pulse_freq_ramsey', 'blue_heat_scan_pulse_freq_ramsey'), 
#                ('lattice.scripts.experiments.Experiments729.blue_heat_scan_pulse_phase_ramsey', 'blue_heat_scan_pulse_phase_ramsey'),
               
               #('lattice.scripts.experiments.Experiments729.dephasing_scan_duration', 'dephase_scan_duration'),
               #('lattice.scripts.experiments.Experiments729.dephasing_scan_phase', 'dephase_scan_phase'),
               #('lattice.scripts.experiments.Experiments729.dephasing_scan_phase', 'dephase_scan_phase'),
               #('lattice.scripts.experiments.Experiments729.dephasing_scan_duration_Phase', 'dephase_scan_duration'),
               
               ('lattice.scripts.experiments.CalibrationScans.two_line_rabi_flop', 'two_line_rabi_flop'),
               ('lattice.scripts.experiments.CalibrationScans.scan_sb_cooling_854', 'scan_sb_cooling_854'),
               ('lattice.scripts.experiments.CalibrationScans.scan_sb_cooling_detuning', 'scan_sb_cooling_detuning'),
               ('lattice.scripts.experiments.CalibrationScans.scan_motional_397pulse_width', 'scan_motional_397pulse_width'),
               ('lattice.scripts.experiments.CalibrationScans.scan_motional_ramsey_time', 'scan_motional_ramsey_time'),
               ('lattice.scripts.experiments.CalibrationScans.rabi_excitation_continuous', 'rabi_excitation_continuous'),
               ('lattice.scripts.experiments.CalibrationScans.setup_dt', 'setup_dt'),
               ('lattice.scripts.experiments.CalibrationScans.setup_local_rotation', 'setup_local_rotation'),
               ('lattice.scripts.experiments.CalibrationScans.calibrate_all_lines', 'calibrate_all_lines'),
               ('lattice.scripts.experiments.CalibrationScans.calibrate_temperature', 'calibrate_temperature'),
               ('lattice.scripts.experiments.CalibrationScans.calibrate_heating_rates', 'calibrate_heating_rates'),
               ('lattice.scripts.experiments.CalibrationScans.pulsed_excitation_scan', 'pulsed_excitation_scan'),
               ('lattice.scripts.experiments.CalibrationScans.ramsey_pulsed_excitation_scan', 'ramsey_pulsed_excitation_scan'),   
               ('lattice.scripts.experiments.Gates.ms_gate', 'ms_gate'),
               ('lattice.scripts.experiments.Gates.ms_scan_ac_stark', 'ms_scan_ac_stark'),
               ('lattice.scripts.experiments.Gates.ms_scan_phase', 'ms_scan_phase'),
               ('lattice.scripts.experiments.Gates.ms_scan_amp', 'ms_scan_amp'),
               ('lattice.scripts.experiments.Gates.ms_scan_local_stark', 'ms_scan_local_stark'),
               ('lattice.scripts.experiments.Gates.ms_scan_local_stark_detuning', 'ms_scan_local_stark_detuning'),
               ('lattice.scripts.experiments.Gates.szx_gate', 'szx'),
               ('lattice.scripts.experiments.Gates.szx_scan_time_phase', 'szx_scan_time_phase'),
               ('lattice.scripts.experiments.Gates.szx_scan_time', 'szx_scan_time'),
               #('lattice.scripts.experiments.Gates.szx_rabi_flop', 'szx_rabi_flop'),
               ('lattice.scripts.experiments.Gates.vaet_scan_delta', 'vaet_scan_delta'),
               ('lattice.scripts.experiments.Gates.vaet_scan_time', 'vaet_scan_time'),
               ('lattice.scripts.experiments.Gates.vaet_scan_local_stark', 'vaet_scan_local_stark'),
               ('lattice.scripts.experiments.Gates.vaet_scan_local_stark_detuning', 'vaet_scan_local_stark_detuning'),
               ('lattice.scripts.experiments.Gates.vaet_scan_ms_detuning', 'vaet_scan_ms_detuning'),
               ('lattice.scripts.experiments.Gates.vaet_parity_flop', 'vaet_parity_flop'),
               ('lattice.scripts.experiments.Gates.vaet_2d_scan', 'vaet_2d_scan'),
               ('lattice.scripts.experiments.Experiments729.setup_experiment', 'setup_experiment'),
               ('lattice.scripts.experiments.Experiments729.sb_track_dual', 'sb_track_dual'),
               ]
    #dictionary in the format class_name : list of non-conflicting class names
    allowed_concurrent = {
    }
