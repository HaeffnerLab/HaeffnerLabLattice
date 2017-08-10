from common.devel.bum.sequences.pulse_sequence import pulse_sequence
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
        print "STARTING STATE PREP"
        print self.start
        
        from subsequences.RepumpD import RepumpD
        from subsequences.DopplerCooling import DopplerCooling
        from subsequences.OpticalPumping import OpticalPumping
        from subsequences.SidebandCooling import SidebandCooling
        from subsequences.EmptySequence import EmptySequence
        
        self.addSequence(RepumpD) # initializing the state of the ion
        self.addSequence(DopplerCooling) 
        
        if self.parameters.StatePreparation.optical_pumping_enable:
            self.addSequence(OpticalPumping)

        if self.parameters.StatePreparation.sideband_cooling_enable:       
            duration_op= self.parameters.SidebandCooling.sideband_cooling_optical_pumping_duration
            for i in range(int(self.parameters.SidebandCooling.sideband_cooling_cycles)):
                self.addSequence(SidebandCooling)
                self.addSequence(OpticalPumping, {'OpticalPumpingContinuous.optical_pumping_continuous_duration':duration_op }) # apply an additional full optical pumping aftereach cycle
                print "Running sideband cooling cycle #"
                print(i) 
                
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : self.parameters.Heating.background_heating_time})


if __name__=='__main__':
    #pv = TreeDict.fromdict({'DopplerCooling.duration':U(5, 'us')})
    #ex = Sequence(pv)
    #psw = pulse_sequence_wrapper('example.xml', pv)
    StatePreparation.execute_external(('RabiExcitation.duration', 0, 5, 5, 'ms'))
