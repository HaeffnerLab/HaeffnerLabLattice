from common.devel.bum.sequences import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict

class PulsedExcitation(pulse_sequence):
    
    name = 'PulsedExcitation'
                            #(self, scan_param, minim, maxim, steps, unit)
    scannable_params = {
        'Motion_Analysis.scan_frequency':  (-10, 10, 1, 'kHz')
              }

    show_params= ['Motion_Analysis.amplitude_397',
                  'Motion_Analysis.excitation_enable',
                  'Motion_Analysis.pulse_width_397',
                  'Excitation_729.channel_729',
                  'Excitation_729.bichro',
                  'Spectrum.sideband_duration',
                  'Spectrum.sideband_amplitude',
                  'Spectrum.line_selection',
                  'Spectrum.sideband_selection',
                  'Spectrum.sideband_order',
                  'StatePreparation.sideband_cooling_enable'
                  ]

    def sequence(self):
        
        from PulseSequences2.subsequences import RepumpD
        from PulseSequences2.subsequences import DopplerCooling
        from PulseSequences2.subsequences import OpticalPumping
        from PulseSequences2.subsequences import SidebandCooling
        from PulseSequences2.subsequences import motion_analysis
        from PulseSequences2.subsequences import RabiExcitation
        from PulseSequences2.subsequences import StateReadout
        
        ## calculate the scan params
        freq_729= self.parameters.Excitation_729.Carrirer[self.parameters.Spectrum.line_selection,self.parameters.Spectrum.sideband_selection,self.parameters.Spectrum.sideband_order]         
        amp=self.parameters.Spectrum.sideband_amplitude
        duration=self.parameters.Spectrum.sideband_duration

        
        self.addSequence(RepumpD) # initializing the state of the ion
        self.addSequence(DopplerCooling) 
        
        if self.parameters.StatePreparation.optical_pumping_enable:
            self.addSequence(OpticalPumping)

        if self.parameters.StatePreparation.sideband_cooling_enable:       
            duration_op= self.parameters.SidebandCooling.sideband_cooling_optical_pumping_duration
            for i in range(self.SidebandCooling.sideband_cooling_cycles):
                self.addSequence(SidebandCooling)
                self.addSequence(OpticalPumping, {'OpticalPumping.optical_pumping_duration':duration_op }) # apply an additional full optical pumping aftereach cycle
                #print(i)  
             
                    
        
        
        if self.parameters.Motion_Analysis.excitation_enable:
            self.addSequence(motion_analysis)
            self.addSequence(OpticalPumping)
                       
              
        self.addSequence(RabiExcitation,{'Excitation_729.rabi_excitation_frequency': freq_729,'Excitation_729.rabi_excitation_amplitude': amp ,'Excitation_729.rabi_excitation_duration': duration })
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

