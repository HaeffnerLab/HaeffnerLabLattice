from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from OpticalPumping import optical_pumping
from SidebandCoolingContinuous import sideband_cooling_continuous
from SidebandCoolingPulsed import sideband_cooling_pulsed

class sideband_cooling(pulse_sequence):
    
    required_parameters = [
                           'sideband_cooling_cycles',
                           'sideband_cooling_continuous',
                           'sideband_cooling_pulsed',
                           'sideband_cooling_duration_729_increment_per_cycle',
                           'sideband_cooling_optical_pumping_duration',
                           'sideband_cooling_continuous_duration',
                           'sideband_cooling_pulsed_duration_729',
                           ]
    
    required_subsequences = [sideband_cooling_continuous, sideband_cooling_pulsed, optical_pumping]
    
    def sequence(self):
        '''
        sideband cooling pulse sequence consists of multiple sideband_cooling_cycles where each cycle consists 
        of a period of sideband cooling followed by continuous optical pumping. 
        
        sideband cooling can be either pulsed or continuous 
        '''
        self.check_valid_selelction()
        if self.sideband_cooling_continuous:
            cooling = sideband_cooling_continuous
            duration_key = 'sideband_cooling_continuous_duration'
            cooling_replace = {
                               'sideband_cooling_continuous_duration':self.sideband_cooling_continuous_duration
                               }
        else:
            cooling = sideband_cooling_pulsed
            duration_key = 'sideband_cooling_pulsed_duration_729'
            cooling_replace = {
                                'sideband_cooling_pulsed_duration_729':self.sideband_cooling_pulsed_duration_729
                               }
        optical_pump_replace = {
                                'optical_pumping_continuous':True,
                                'optical_pumping_continuous_duration':self.sideband_cooling_optical_pumping_duration
                                
                                }
        for i in range(int(self.sideband_cooling_cycles)):
            #each cycle, increment the 729 duration
            cooling_replace[duration_key] +=  self.sideband_cooling_duration_729_increment_per_cycle
            self.addSequence(cooling, **cooling_replace)
            self.addSequence(optical_pumping, **optical_pump_replace)
    
    def check_valid_selelction(self):
        #^does xor, because exactly one has to be true
        if not self.sideband_cooling_continuous ^ self.sideband_cooling_pulsed:
            raise Exception ("Incorrect sideband cooling type selected")