from lattice.scripts.PulseSequences.blue_heat_ramsey import blue_heat_ramsey
from lattice.scripts.experiments.Experiments729.excitation_729 import excitation_729

class excitation_blue_heat_ramsey(excitation_729):
    
    name = 'ExcitationRamsey'
    
    required_parameters = [('OpticalPumping','frequency_selection'),
                           ('OpticalPumping','manual_frequency_729'),
                           ('OpticalPumping','line_selection'),
                           
                           ('SidebandCooling','frequency_selection'),
                           ('SidebandCooling','manual_frequency_729'),
                           ('SidebandCooling','line_selection'),
                           ('SidebandCooling','sideband_selection'),
                           ('TrapFrequencies','axial_frequency'),
                           ('TrapFrequencies','radial_frequency_1'),
                           ('TrapFrequencies','radial_frequency_2'),
                           ('TrapFrequencies','rf_drive_frequency'),
                           
                           ('StateReadout', 'repeat_each_measurement'),
                           ('StateReadout', 'state_readout_threshold'),
                           ('StateReadout', 'use_camera_for_readout'),
                           ('StateReadout', 'state_readout_duration'),
                           
                           ('IonsOnCamera','ion_number'),
                           ('IonsOnCamera','vertical_min'),
                           ('IonsOnCamera','vertical_max'),
                           ('IonsOnCamera','vertical_bin'),
                           ('IonsOnCamera','horizontal_min'),
                           ('IonsOnCamera','horizontal_max'),
                           ('IonsOnCamera','horizontal_bin'),
                           
                           ('IonsOnCamera','fit_amplitude'),
                           ('IonsOnCamera','fit_background_level'),
                           ('IonsOnCamera','fit_center_horizontal'),
                           ('IonsOnCamera','fit_center_vertical'),
                           ('IonsOnCamera','fit_rotation_angle'),
                           ('IonsOnCamera','fit_sigma'),
                           ('IonsOnCamera','fit_spacing'),
                           ]
    pulse_sequence = blue_heat_ramsey
    required_parameters.extend(pulse_sequence.all_required_parameters())
    #removing pulse sequence items that will be calculated in the experiment and do not need to be loaded
    required_parameters.remove(('OpticalPumping', 'optical_pumping_frequency_729'))
    required_parameters.remove(('SidebandCooling', 'sideband_cooling_frequency_729'))
    
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = excitation_blue_heat_ramsey(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)