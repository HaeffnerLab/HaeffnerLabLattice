from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from lattice.scripts.PulseSequences.subsequences.DopplerCooling import doppler_cooling

class state_readout(pulse_sequence):
    
    
    required_parameters = [
                'state_readout_frequency_397', 
                'state_readout_amplitude_397', 
                'state_readout_frequency_866', 
                'state_readout_amplitude_866', 
                'state_readout_duration',
                ]

    required_subsequences = [doppler_cooling]
    
    def sequence(self):
        
        replace = {
                   'doppler_cooling_frequency_397':self.state_readout_frequency_397,
                   'doppler_cooling_amplitude_397':self.state_readout_amplitude_397,
                   'doppler_cooling_frequency_866':self.state_readout_frequency_866,
                   'doppler_cooling_amplitude_866':self.state_readout_amplitude_866,
                   'doppler_cooling_duration':self.state_readout_duration,
                   }
        self.addSequence(doppler_cooling, **replace)
        self.addTTL('ReadoutCount', self.start, self.state_readout_duration)