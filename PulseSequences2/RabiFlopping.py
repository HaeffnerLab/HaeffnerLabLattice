from common.devel.bum.sequences import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict

class RabiFlopping(pulse_sequence):
    
    name = 'RabiFlopping'
                            #(self, scan_param, minim, maxim, steps, unit)
    scannable_params = {
        'RabiFlopping.manual_scan':  (0, 50, 2.5, 'us')
              }

    show_params= ['Excitation_729.channel_729',
                  'Excitation_729.bichro',
                  'RabiFlopping.line_selection',
                  'RabiFlopping.rabi_amplitude_729',
                  'RabiFlopping.sideband_selection',
                  'RabiFlopping.sideband_order'
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
        freq_729= self.parameters.Excitation_729.Carrirer[self.parameters.RabiFlopping.line_selection,self.parameters.RabiFlopping.sideband_selection,self.parameters.RabiFlopping.sideband_order]
        amp=self.parameters.RabiFlopping.rabi_amplitude_729
        duration=self.parameters.RabiFlopping.manual_scan
        
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
    RabiFlopping.execute_external(('RabiFlopping.manual_scan', 0, 50,2.5, 'us'))
