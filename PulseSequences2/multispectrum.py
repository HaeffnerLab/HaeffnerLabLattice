from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict

class SpectrumRed(pulse_sequence):
    scannable_params = {
        #'Spectrum.carrier_detuning':  [(-50, 50, 100, 'kHz'), 'window']
        'Spectrum.carrier_detuning' : [(-150, 150, 150., 'kHz'),'car1'],
        'Spectrum.sideband_detuning' :[(-50, 50, 50., 'kHz'),'car1']
         }
        
    def sequence(self):
        
        from StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
           
        ## calculate the scan params
        spc = self.parameters.Spectrum
        order = -1
        freq_729=self.calc_freq(spc.line_selection, spc.selection_sideband ,int(order))
        
        freq_729=freq_729 + spc.sideband_detuning
        
        print "Spectrum scan"
        print "729 freq.{}".format(freq_729)
        
        amp=spc.manual_amplitude_729
        duration=spc.manual_excitation_time
                
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
    

    
class SpectrumBlue(pulse_sequence):
    scannable_params = {
        #'Spectrum.carrier_detuning':  [(-50, 50, 100, 'kHz'), 'window']
        'Spectrum.carrier_detuning' : [(-150, 150, 50., 'kHz'),'car2']
        
              }
    
    def sequence(self):
        
        from StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
           
        ## calculate the scan params
        spc = self.parameters.Spectrum
        order = +1
        freq_729=self.calc_freq(spc.line_selection, spc.selection_sideband ,int(order))
        
        freq_729=freq_729 + spc.sideband_detuning
        
        print "Spectrum scan"
        print "729 freq.{}".format(freq_729)
        
        amp=spc.manual_amplitude_729
        duration=spc.manual_excitation_time
                
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

        
class MultiSpectrum(pulse_sequence):
    is_composite = True
    
    sequences = [SpectrumRed, SpectrumBlue]

    show_params= ['Excitation_729.channel_729',
                  'Excitation_729.bichro',
                  'Spectrum.manual_amplitude_729',
                  'Spectrum.manual_excitation_time',
                  'Spectrum.line_selection',
                  'Spectrum.selection_sideband',
                  'Spectrum.order'
                  ]
    