from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict


class SidebandOptimization(pulse_sequence):
                            
    scannable_params = {'SidebandCooling.sideband_cooling_amplitude_854' : [(-30., -6., 3., 'dBm'), 'current'],
                        'SidebandCooling.stark_shift' : [(-50.0, 50.0, 2.5, 'kHz'), 'current']}

    show_params= ['Excitation_729.channel_729',
                  'Excitation_729.bichro',
                  'SidebandCooling.line_selection',
                  'SidebandCooling.sideband_cooling_amplitude_729',
                  'SidebandCooling.sideband_cooling_amplitude_854',
                  'SidebandCooling.sideband_cooling_amplitude_866',
                  'SidebandCooling.selection_sideband',
                  'SidebandCooling.order',
                  'SidebandCooling.stark_shift',
                  'SidebandCooling.cooling_cycles',
                  'RabiFlopping.rabi_amplitude_729',
                  'RabiFlopping.duration',
                  'RabiFlopping.line_selection',
                  'RabiFlopping.selection_sideband',
                  'RabiFlopping.order',
                  'StatePreparation.channel_729',
                  'StatePreparation.optical_pumping_enable',
                  'StatePreparation.sideband_cooling_enable']
    
    
    def sequence(self):
        from StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
        
        
        ## calculate the scan params
        rf = self.parameters.RabiFlopping 
        freq_729=self.calc_freq(rf.line_selection , rf.selection_sideband , rf.order)
        print "321321"
        print "freq 729", freq_729 
        self.end = U(10., 'us')      
        
        self.addSequence(TurnOffAll)
        self.addSequence(StatePreparation)       
        self.addSequence(RabiExcitation,{'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': rf.rabi_amplitude_729,
                                         'Excitation_729.rabi_excitation_duration':  rf.duration })
        self.addSequence(StateReadout)
        
        