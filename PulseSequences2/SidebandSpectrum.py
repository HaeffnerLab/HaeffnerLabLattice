from common.devel.bum.sequences import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict

class SidebandSpectrum(pulse_sequence):
    
    name = 'Spectrum729'
                            #(self, scan_param, minim, maxim, steps, unit)
    scannable_params = {
        'Spectrum.sideband_detuning':  (-50, 50, 100, 'kHz')
              }

    show_params= ['Excitation_729.channel_729',
                  'Excitation_729.bichro',
                  'Spectrum.sideband_duration',
                  'Spectrum.sideband_amplitude',
                  'Spectrum.line_selection',
                  'Spectrum.sideband_selection',
                  'Spectrum.sideband_order'
                  ]
    
 

    def sequence(self):
        
        from PulseSequences2 import StatePreparation
        from PulseSequences2.subsequences import RabiExcitation
        from PulseSequences2.subsequences import StateReadout
        
        ## calculate the 729 params
        carrier=self.parameters.Spectrum.line_selection
        side_band=self.parameters.Spectrum.sideband_selection
        order=self.parameters.Spectrum.sideband_order 
        freq_729 = self.calc_freq(carrier, side_band,order)
                      
        amp=self.parameters.Spectrum.sideband_amplitude
        duration=self.parameters.Spectrum.sideband_duration
                
        #if p.Motion_Analysis.excitation_enable:
        #    self.addSequence(motion_analysis)
        
        # building the sequence               
        self.addSequence(StatePreparation)         
        self.addSequence(RabiExcitation,{'Excitation_729.rabi_excitation_frequency': freq_729,
                                         'Excitation_729.rabi_excitation_amplitude': amp,
                                         'Excitation_729.rabi_excitation_duration': duration })
        self.addSequence(StateReadout)
        
    @classmethod
    def run_initial(cls,cxn, parameters_dict):
        print "Switching the 866DP to auto mode"
        cxn.pulser.switch_auto('866DP')
        
    @classmethod
    def run_in_loop(cls,cxn, parameters_dict, data, x):
        #print "Running in loop Rabi_floping"
        pass
    
    @classmethod
    def run_finally(cls,cxn, parameters_dict, data, x):
        print "switching the 866 back to ON"
        cxn.pulser.switch_manual('866DP', True)
        
        

if __name__=='__main__':
    #pv = TreeDict.fromdict({'DopplerCooling.duration':U(5, 'us')})
    #ex = Sequence(pv)
    #psw = pulse_sequence_wrapper('example.xml', pv)
    SidebandSpectrum.execute_external(('Spectrum.carrirer_detuning', -50, 50,100, 'kHz'))
