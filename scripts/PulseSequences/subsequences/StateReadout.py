from lattice.scripts.PulseSequences.PulseSequence import PulseSequence
from lattice.scripts.PulseSequences.subsequences.DopplerCooling import doppler_cooling

class state_readout(PulseSequence):
    
    def configuration(self):
        config = [
                'state_readout_frequency_397', 
                'state_readout_amplitude_397', 
                'state_readout_frequency_866', 
                'state_readout_amplitude_866', 
                'state_readout_duration',
                ]
        return config
    
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