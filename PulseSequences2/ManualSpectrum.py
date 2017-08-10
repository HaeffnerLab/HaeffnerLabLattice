from common.devel.bum.sequences import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict

class ManualSpectrum(pulse_sequence):
    
    name = 'Spectrum729'
                            #(self, scan_param, minim, maxim, steps, unit)
    scannable_params = {
        'Spectrum.manual_freq':  (-20,20, 2000, 'MHz')
              }

    show_params= ['Excitation_729.channel_729',
                  'Excitation_729.bichro',
                  'Spectrum.manual_duration',
                  'Spectrum.manual_amplitude',
                     ]
    
    def run_initial(self):
        pass

    def sequence(self):
        
        from PulseSequences2 import StatePreparation
        from PulseSequences2.subsequences import RabiExcitation
        from PulseSequences2.subsequences import StateReadout
        
               
        ## calculate the scan params
        freq_729 = U(220,'MHz')+ self.parameters.Spectrum.manual_freq           
        amp=self.parameters.Spectrum.manual_amplitude
        duration=self.parameters.Spectrum.manual_duration
        
        # building the sequence
        self.addSequence(StatePreparation)                 
        self.addSequence(RabiExcitation,{'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': amp ,
                                         'Excitation_729.rabi_excitation_duration': duration })
        self.addSequence(StateReadout)
        
        

if __name__=='__main__':
    #pv = TreeDict.fromdict({'DopplerCooling.duration':U(5, 'us')})
    #ex = Sequence(pv)
    #psw = pulse_sequence_wrapper('example.xml', pv)
    ManualSpectrum.execute_external(('Spectrum.carrirer_detuning', -50, 50,100, 'kHz'))
