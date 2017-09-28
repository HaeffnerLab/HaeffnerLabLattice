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


    def sequence(self):
        
        from StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
           
        ## calculate the scan params
        freq_729 = self.parameters.Spectrum.manual_freq           
        amp=self.parameters.Spectrum.manual_amplitude
        duration=self.parameters.Spectrum.manual_duration
        
        print "Manual spectrum scan"
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

#if __name__=='__main__':
    #pv = TreeDict.fromdict({'DopplerCooling.duration':U(5, 'us')})
    #ex = Sequence(pv)
    #psw = pulse_sequence_wrapper('example.xml', pv)
#    ManualSpectrum.execute_external(('Spectrum.carrirer_detuning', -50, 50,100, 'kHz'))
