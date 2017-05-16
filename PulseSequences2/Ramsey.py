from common.devel.bum.sequences import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import numpy as np

class Ramsey(pulse_sequence):
    
    #name = 'Ramsey'

    scannable_params = {
        'RamseyScanGap.scangap': (0, 10.0, 0.1, 'ms'),
        'RamseyScanPhase.scanphase': (0, 360., 15, 'deg')
        }

    show_params= ['RamseyScanGap.scangap',
                  'RamseyScanPhase.scanphase',
                  'RamseyScanGap.detunign',
                  need to work on this
                  'Ramsey.channel_729',
                  'Ramsey.rabi_pi_time',
                  'Spectrum.line_selection',
                  'Spectrum.sideband_selection']

    def sequence(self):
        
        from PulseSequences2.subsequences import RepumpD
        from PulseSequences2.subsequences import DopplerCooling
        from PulseSequences2.subsequences import OpticalPumping
        from PulseSequences2.subsequences import SidebandCooling
        from PulseSequences2.subsequences import GlobalRotation
        from PulseSequences2.subsequences import EmptySequence 
        from PulseSequences2.subsequences import StateReadout
        
                ## calculate the scan params
        freq_729= self.parameters.Excitation_729.Carrirer[self.parameters.Spectrum.line_selection,self.parameters.Spectrum.sideband_selection,self.parameters.Spectrum.sideband_order]
        freq_729 +=  self.parameters.Spectrum.sideband_detuning           
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
        ### end of state preparation
        
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : self.parameters.Heating.background_heating_time})
        
        #def addSequence(self, sequence, replacement_dict = TreeDict(), position = None):
            # {'key_to_replace': value_to_put_in
        # apply the first pi/2            
        self.addSequence(GlobalRotation, { "GlobalRotation.angle": np.pi/2.0, "GlobalRotation.phase": 0.0})
        self.addSequence(EmptySequence,  { "EmptySequence.empty_sequence_duration" : self.Ramsey.ramsey_time})
        self.addSequence(GlobalRotation, { "GlobalRotation.angle": np.pi/2.0, "GlobalRotation.phase": self.Ramsey.second_pulse_phase })
        self.addSequence(StateReadout)
        

if __name__=='__main__':
    #pv = TreeDict.fromdict({'DopplerCooling.duration':U(5, 'us')})
    #ex = Sequence(pv)
    #psw = pulse_sequence_wrapper('example.xml', pv)
    print 'executing a scan gap'
    Ramsey.execute_external(('Ramsey.ramsey_time', 0, 10.0, 0.1, 'ms'))
