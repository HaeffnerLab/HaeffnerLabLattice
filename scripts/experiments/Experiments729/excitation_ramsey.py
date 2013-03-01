from lattice.scripts.PulseSequences.ramsey import ramsey
from excitation_729 import excitation_729

class excitation_ramsey(excitation_729):
    
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
                           ]
    pulse_sequence = ramsey
    required_parameters.extend(pulse_sequence.required_parameters)
    #removing pulse sequence items that will be calculated in the experiment and do not need to be loaded
    required_parameters.remove(('OpticalPumping', 'optical_pumping_frequency_729'))
    required_parameters.remove(('SidebandCooling', 'sideband_cooling_frequency_729'))
    
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = excitation_ramsey(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)