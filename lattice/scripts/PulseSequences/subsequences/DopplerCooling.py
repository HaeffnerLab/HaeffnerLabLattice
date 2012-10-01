from scripts.PulseSequences.PulseSequence import PulseSequence

class doppler_cooling(PulseSequence):
    
    def configuration(self):
        
        config = [
                'doppler_cooling_frequency_397', 
                'doppler_cooling_amplitude_397', 
                'doppler_cooling_frequency_866', 
                'doppler_cooling_amplitude_866', 
                'doppler_cooling_duration',
                ]
        return config
    
    def sequence(self):
        pulses = self.dds_pulses
        
        #offset
        from labrad import types as T
        offset = T.Value(100, 'us')
        pulses.append( ('110DP',self.start, self.p.doppler_cooling_duration, self.p.doppler_cooling_frequency_397, self.p.doppler_cooling_amplitude_397) )
        #pulses.append( ('866DP',self.start, self.p.doppler_cooling_duration, self.p.doppler_cooling_frequency_866, self.p.doppler_cooling_amplitude_866) )
        pulses.append( ('866DP',self.start, self.p.doppler_cooling_duration + offset, self.p.doppler_cooling_frequency_866, self.p.doppler_cooling_amplitude_866) )
        self.end = self.start + self.p.doppler_cooling_duration + offset