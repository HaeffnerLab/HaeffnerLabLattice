from common.devel.bum.sequences import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict

class StatePreparation(pulse_sequence):
    
    #name = 'State preparation'

    scannable_params = {
                        }

    show_params= ['DopplerCooling.duration',
                  'Spectrum.line_selection',
                  'sideband_selection']

    def sequence(self):
        
        from PulseSequences2.subsequences import RepumpD
        from PulseSequences2.subsequences import DopplerCooling
        from PulseSequences2.subsequences import OpticalPumping
        from PulseSequences2.subsequences import SidebandCooling
        from PulseSequences2.subsequences import EmptySequence
        from PulseSequences2.subsequences import RabiExcitation
        from PulseSequences2.subsequences import StateReadout
        
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


if __name__=='__main__':
    #pv = TreeDict.fromdict({'DopplerCooling.duration':U(5, 'us')})
    #ex = Sequence(pv)
    #psw = pulse_sequence_wrapper('example.xml', pv)
    StatePreparation.execute_external(('RabiExcitation.duration', 0, 5, 5, 'ms'))
