from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict


class SidebandOptimization(pulse_sequence):
                            
    scannable_params = {'SidebandCooling.sideband_cooling_amplitude_854' : [(-50., -6., 3., 'dBm'), 'current'],
                        'SidebandCooling.sideband_cooling_frequency_854' : [(79500, 80500, 50, 'kHz'), 'current']}

    show_params= ['Excitation_729.channel_729',
                  'Excitation_729.bichro',
                  'SidebandCooling.line_selection',
                  'SidebandCooling.sideband_cooling_amplitude_729',
                  'SidebandCooling.sideband_cooling_amplitude_854',
                  'SidebandCooling.sideband_cooling_amplitude_866',
                  'SidebandCooling.sideband_selection',
                  'SidebandCooling.stark_shift',
                  'RabiFlopping.rabi_amplitude_729',
                  'RabiFlopping.duration',
                  'RabiFlopping.line_selection',
                  'RabiFlopping.sideband_selection',
                  'RabiFlopping.sideband_order',
                  'StatePreparation.channel_729',
                  'StatePreparation.optical_pumping_enable',
                  'StatePreparation.sideband_cooling_enable']
    
    
    def sequence(self):
        from StatePreparation import StatePreparation
        from RabiFlopping import RabiFlopping
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
        
        self.end = U(10., 'us')
        
        
        
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)
        
        self.addSequence(RabiFlopping)
        
        self.addSequence(StateReadout)