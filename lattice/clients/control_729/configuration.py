class config_729_hist(object):
    #IDs for signaling
    ID_A = 99999
    ID_B = 99998
    #data vault comment
    dv_parameter = 'Histogram729'
    #semaphore locations
    readout_threshold_dir =  ['729Experiments','readout_threshold']

class state_readout(object):
    #IDs for signaling
    ID = 99993
    
    readout_threshold_dir =  ['729Experiments','readout_threshold']
    readout_time_dir = ['729Experiments','state_readout_duration']
    
    repeat_each_measurement = ['729Experiments','repeat_each_measurement']
    
    state_readout_frequency_397 = ['729Experiments','state_readout_frequency_397']
    state_readout_amplitude_397 = ['729Experiments','state_readout_amplitude_397']
    state_readout_frequency_866 = ['frequency_866']
    state_readout_amplitude_866 = ['729Experiments','state_readout_amplitude_866']

class config_729_optical_pumping(object):
    #IDs for signaling
    ID = 99997
    #semaphore locations
    optical_pumping_amplitude_729 = ['729Experiments','optical_pumping_amplitude_729']
    optical_pumping_amplitude_854 = ['729Experiments','optical_pumping_amplitude_854']
#    optical_pumping_continuous = ['729Experiments','optical_pumping_continuous']
    optical_pumping_continuous_duration = ['729Experiments','optical_pumping_continuous_duration']
    optical_pumping_continuous_pump_additional = ['729Experiments','optical_pumping_continuous_repump_additional']
#    optical_pumping_pulsed = ['729Experiments','optical_pumping_pulsed']
    optical_pumping_enable = ['729Experiments','optical_pumping_enable']
    optical_pumping_frequency = ['729Experiments','optical_pumping_frequency']
#    optical_pumping_pulsed_cycles = ['729Experiments','optical_pumping_pulsed_cycles']
#    optical_pumping_pulsed_duration_729 = ['729Experiments','optical_pumping_pulsed_duration_729']
#    optical_pumping_pulsed_duration_854 = ['729Experiments','optical_pumping_pulsed_duration_854']
    
class config_729_spectrum(object):
    #IDs for signaling
    ID = 99996
    #semaphore locations
    excitation_time = ['729Experiments','Spectrum','excitation_time']
    frequencies = ['729Experiments','Spectrum','frequencies']
    spectrum_amplitude_729 = ['729Experiments','Spectrum','spectrum_amplitude_729']

class config_729_rabi_flop(object):
    #IDs for signaling
    ID = 99995
    #semaphore locations 
    frequency = ['729Experiments','RabiFlopping','frequency']
    excitation_times = ['729Experiments','RabiFlopping','excitation_times']
    rabi_amplitude_729 = ['729Experiments','RabiFlopping','rabi_amplitude_729']

class config_729_general_parameters(object):
    #IDs for signaling
    ID = 99994
    #semaphore locations 
    heating_duration = ['729Experiments','heating_time']
    amplitude_854 = ['729Experiments','amplitude_854']
#    enable_calibration = ['729Experiments','enable_calibration_double_pass_729']
#    calibration_reduction = ['729Experiments','calibration_double_pass_729_reduction']
    repeat_each_measurement = ['729Experiments','repeat_each_measurement']
    repump_d_duration = ['729Experiments','repump_d_duration']
    state_readout_frequency_397 = ['729Experiments','state_readout_frequency_397']
    state_readout_amplitude_397 = ['729Experiments','state_readout_amplitude_397']
    