from scripts.PulseSequences.PulseSequence import PulseSequence

class doppler_cooling(PulseSequence):
    
    
    @classmethod
    def required_parameters(cls):
        
        config = [
                'doppler_cooling_frequency_397', 
                'doppler_cooling_amplitude_397', 
                'doppler_cooling_frequency_866', 
                'doppler_cooling_amplitude_866', 
                'doppler_cooling_duration',
                'doppler_cooling_repump_additional'
                ]
        return config
    
    def sequence(self):
        pulses = self.dds_pulses
        repump_duration = self.doppler_cooling_duration + self.doppler_cooling_repump_additional
        pulses.append( ('110DP',self.start, self.doppler_cooling_duration, self.doppler_cooling_frequency_397, self.doppler_cooling_amplitude_397) )
        pulses.append( ('866DP',self.start, repump_duration, self.doppler_cooling_frequency_866, self.doppler_cooling_amplitude_866) )
        self.end = self.start + repump_duration