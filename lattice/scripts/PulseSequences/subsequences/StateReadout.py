from scripts.PulseSequences.PulseSequence import PulseSequence
from scripts.PulseSequences.subsequences.DopplerCooling import doppler_cooling

class state_readout(PulseSequence):
    
    @staticmethod
    def configuration():
        config = [
                'state_readout_frequency_397', 
                'state_readout_amplitude_397', 
                'state_readout_frequency_866', 
                'state_readout_amplitude_866', 
                'state_readout_duration',
                ]
        return config
    
    @staticmethod
    def needs_subsequences():
        return [doppler_cooling]
    
    def sequence(self):
        
        replace = {
                   'doppler_cooling_frequency_397':self.p.state_readout_frequency_397,
                   'doppler_cooling_amplitude_397':self.p.state_readout_amplitude_397,
                   'doppler_cooling_frequency_866':self.p.state_readout_frequency_866,
                   'doppler_cooling_amplitude_866':self.p.state_readout_amplitude_866,
                   'doppler_cooling_duration':self.p.state_readout_duration,
                   }
        
        self.addSequence(doppler_cooling, **replace)
        self.ttl_pulses.append(('ReadoutCount', self.start, self.p.state_readout_duration))