from scripts.PulseSequences.configuration import DopplerCoolingConfig as c
from scripts.PulseSequences.SemaphoreSequence import SemaphoreSequence

class DopplerCooling(SemaphoreSequence):
    
    def semaphore_configuration(self):
        return c.params
        
    def sequence(self):
        blue_dds_pulses = []
        red_dds_pulses = []
        dur = self.p.doppler_cooling_duration
        blue_dds_pulses.append( (self.start, self.p.doppler_cooling_frequency_397, self.p.doppler_cooling_amplitude_397) )
        blue_dds_pulses.append( (self.start + dur, self.p.doppler_cooling_frequency_397, -63.0) )
        red_dds_pulses.append(  (self.start, self.p.doppler_cooling_frequency_866, self.p.doppler_cooling_amplitude_866) )
        red_dds_pulses.append(  (self.start + dur, self.p.doppler_cooling_frequency_866, -63.0) )
        self.end = self.start + dur
        for pulses in [('110DP', blue_dds_pulses), ('866DP', red_dds_pulses)]:
            self.dds_pulses.append(pulses)