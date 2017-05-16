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
        
        from PulseSequences2.subsequences import RepumpD
        from PulseSequences2.subsequences import DopplerCooling
        from PulseSequences2.subsequences import OpticalPumping
        from PulseSequences2.subsequences import SidebandCooling
        from PulseSequences2.subsequences import EmptySequence
        from PulseSequences2.subsequences import RabiExcitation
        from PulseSequences2.subsequences import StateReadout
        
        ## calculate the scan params
        freq_729 = U(220,'MHz')+ self.parameters.Spectrum.manual_freq           
        amp=self.parameters.Spectrum.manual_amplitude
        duration=self.parameters.Spectrum.manual_duration
        
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
             
                    
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : self.parameters.Heating.background_heating_time})
        
        #if p.Motion_Analysis.excitation_enable:
        #    self.addSequence(motion_analysis)
                       
              
        self.addSequence(RabiExcitation,{'Excitation_729.rabi_excitation_frequency': freq_729,'Excitation_729.rabi_excitation_amplitude': amp ,'Excitation_729.rabi_excitation_duration': duration })
        self.addSequence(StateReadout)
        
        

if __name__=='__main__':
    #pv = TreeDict.fromdict({'DopplerCooling.duration':U(5, 'us')})
    #ex = Sequence(pv)
    #psw = pulse_sequence_wrapper('example.xml', pv)
    ManualSpectrum.execute_external(('Spectrum.carrirer_detuning', -50, 50,100, 'kHz'))
