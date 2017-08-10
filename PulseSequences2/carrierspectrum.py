#!scriptscanner

from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict

class CarrierSpectrum(pulse_sequence):
    
    #name = 'Spectrum729'
                            #(self, scan_param, minim, maxim, steps, unit)
    scannable_params = {
        #'Spectrum.carrier_detuning':  [(-50, 50, 100, 'kHz'), 'window']
        'Spectrum.carrier_detuning': (-50, 50, 100, 'kHz')
              }

    show_params= ['Excitation_729.channel_729',
                  'Excitation_729.bichro',
                  #'Spectrum.carrirer_duration',
                  #'Spectrum.carrirer_amplitude',
                  #'Spectrum.line_selection',   
                  ]
   
    def run_initial(self):
        pass

    def sequence(self):
        
        from PulseSequences2 import StatePreparation
        from PulseSequences2.subsequences import RabiExcitation
        from PulseSequences2.subsequences import StateReadout
        # calculate the scan params
        carrier=self.parameters.Spectrum.line_selection
        sideband=self.parameters.Spectrum.sideband_selection
        #order=self.parameters.Spectrum.sideband_order
        #freq_729 = self.calc_freq(carrier, sideband,order)
        freq_729 = self.calc_freq(carrier, 0)       
        amp=self.parameters.Spectrum.carrirer_amplitude
        duration=self.parameters.Spectrum.carrier_duration
        
        # building the sequence                       
        self.addSequence(StatePreparation)        
        self.addSequence(RabiExcitation,{'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': amp,
                                         'Excitation_729.rabi_excitation_duration': duration })
        self.addSequence(StateReadout)
        

if __name__=='__main__':
    #pv = TreeDict.fromdict({'DopplerCooling.duration':U(5, 'us')})
    #ex = Sequence(pv)
    #psw = pulse_sequence_wrapper('example.xml', pv)
    CarrierSpectrum.execute_external(('Spectrum.carrirer_detuning', -50, 50,100, 'kHz'))
