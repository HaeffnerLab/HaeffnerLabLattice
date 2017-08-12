#!scriptscanner

from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict

class Spectrum(pulse_sequence):
    
    name = 'Spectrum729'
                            #(self, scan_param, minim, maxim, steps, unit)
    scannable_params = {
        #'Spectrum.carrier_detuning':  [(-50, 50, 100, 'kHz'), 'window']
        'Spectrum.carrier_detuning' : (-50, 50, 100, 'kHz'),
        'Spectrum.sideband_detuning' :(-50, 50, 100, 'kHz')
              }

    show_params= ['Excitation_729.channel_729',
                  'Excitation_729.bichro',
                  'Spectrum.carrirer_duration',
                  'Spectrum.carrirer_amplitude',
                  'Spectrum.line_selection',   
                  ]
   
    def run_initial(self):
        pass

    def sequence(self):
        
        from StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
           
        ## calculate the scan params
        spc = self.parameters.Spectrum   
        
        if spc.selection_sideband == "off":         
            freq_729=self.calc_freq(spc.line_selection)
        else:
            freq_729=self.calc_freq(spc.line_selection, spc.selection_sideband ,int(spc.order))
        
        freq_729=freq_729 + spc.carrier_detuning + spc.sideband_detuning
        
        print "Spectrum scan"
        print "729 freq.{}".format(freq_729)
        
                
        # building the sequence
        # needs a 10 micro sec for some reason
        self.end = U(10., 'us')
        #self.addSequence(TurnOffAll)           
        self.addSequence(StatePreparation)      
        self.addSequence(RabiExcitation,{'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': amp,
                                         'Excitation_729.rabi_excitation_duration':  duration })
        self.addSequence(StateReadout)