class config(object):

    #list in the format (import_path, class_name)
    scripts = [
               ('lattice.scripts.experiments.FFT.fft_spectrum', 'fft_spectrum'), 
#                ('lattice.scripts.experiments.FFT.fft_peak_area', 'fft_peak_area'), 
#                ('lattice.scripts.experiments.FFT.fft_hv_scan', 'fft_hv_scan'), 
#                ('lattice.scripts.experiments.Misc.set_high_volt', 'set_high_volt'), 
               ('lattice.scripts.experiments.Misc.set_linetrigger_offset', 'set_linetrigger_offset'), 
               ('lattice.scripts.experiments.CavityScan.scan_cavity', 'scan_cavity'), 
               ('lattice.scripts.experiments.CavityScan.scan_cavity_397', 'scan_cavity_397'), 
               ('lattice.scripts.experiments.CavityScan.scan_cavity_866', 'scan_cavity_866'), 
#                ('lattice.scripts.experiments.Experiments729.excitation_729', 'excitation_729'), 
               ('lattice.scripts.experiments.Experiments729.spectrum', 'spectrum'), 
               ('lattice.scripts.experiments.Experiments729.rabi_flopping', 'rabi_flopping'), 
               ('lattice.scripts.experiments.Experiments729.drift_tracker', 'drift_tracker'), 
#                ('lattice.scripts.experiments.Experiments729.excitation_ramsey', 'excitation_ramsey'), 
               ('lattice.scripts.experiments.Experiments729.ramsey_scangap', 'ramsey_scangap'), 
               ('lattice.scripts.experiments.Experiments729.ramsey_scanphase', 'ramsey_scanphase'), 
#                ('lattice.scripts.experiments.Experiments729.excitation_rabi_tomography', 'excitation_rabi_tomography'), 
               ('lattice.scripts.experiments.Experiments729.rabi_tomography', 'rabi_tomography'), 
               ('lattice.scripts.experiments.BareLineScan.BareLineScanRed', 'bare_line_scan_red'), 
               ('lattice.scripts.experiments.BareLineScan.BareLineScan', 'bare_line_scan'),
               ('lattice.scripts.experiments.AO_calibration.AO_calibration', 'AO_calibration'), 
               ('lattice.scripts.experiments.Experiments729.drift_tracker_ramsey', 'drift_tracker_ramsey'), 
               ('lattice.scripts.experiments.Experiments729.blue_heat_rabi_flopping', 'blue_heat_rabi_flopping'), 
               ('lattice.scripts.experiments.Camera.reference_image', 'reference_camera_image'), 
               ('lattice.scripts.experiments.Lifetime_P.lifetime_p', 'lifetime_p'), 
               ('lattice.scripts.experiments.Experiments729.rabi_flop_scannable', 'rabi_flopping_scannable'), 
               ('lattice.scripts.experiments.Experiments729.blue_heat_spectrum', 'blue_heat_spectrum'), 
               ('lattice.scripts.experiments.Experiments729.blue_heat_scan_delay', 'blue_heat_scan_delay'), 
               ('lattice.scripts.experiments.Experiments729.blue_heat_scan_pulse_freq', 'blue_heat_scan_pulse_freq'), 
               ('lattice.scripts.experiments.Experiments729.blue_heat_scan_pulse_freq_ramsey', 'blue_heat_scan_pulse_freq_ramsey'), 
               ('lattice.scripts.experiments.Experiments729.blue_heat_scan_pulse_phase_ramsey', 'blue_heat_scan_pulse_phase_ramsey'),
               ('lattice.scripts.experiments.Experiments729.Dephasing_with_729.dephasing_with_729_scan_second_pulse_phase', 'scan_phase_of_second_pulse'),
                ('lattice.scripts.experiments.Experiments729.Dephasing_with_729.dephasing_with_729_scan_second_pulse_duration', 'scan_duration_of_second_pulse'),
               ]
    #dictionary in the format class_name : list of non-conflicting class names
    allowed_concurrent = {
    }