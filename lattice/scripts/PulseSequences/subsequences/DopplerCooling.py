from scripts.PulseSequences.PulseSequence import PulseSequence
from labrad import types as T

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
        blue_dds_pulses = []
        red_dds_pulses = []
        dur = self.p.doppler_cooling_duration
        blue_dds_pulses.append( (self.start, self.p.doppler_cooling_frequency_397, self.p.doppler_cooling_amplitude_397) )
        blue_dds_pulses.append( (self.start + dur, self.p.doppler_cooling_frequency_397, T.Value(-63.0, 'dBm')) )
        red_dds_pulses.append(  (self.start, self.p.doppler_cooling_frequency_866, self.p.doppler_cooling_amplitude_866) )
        red_dds_pulses.append(  (self.start + dur, self.p.doppler_cooling_frequency_866, T.Value(-63.0, 'dBm')) )
        self.end = self.start + dur
        for pulses in [('110DP', blue_dds_pulses), ('866DP', red_dds_pulses)]:
            self.dds_pulses.append(pulses)