from configuration import DopplerCoolingConfig as c
from SemaphoreSequence import SemaphoreSequence

class DopplerCooling(SemaphoreSequence):
    
    def configuration(self):
        return c.params
        
    def sequence(self):
        blue_dds_pulses = []
        red_dds_pulses = []
        blue_dds_pulses.append( (self.start, self.p.doppler_cooling_frequency_397, self.p.doppler_cooling_amplitude_397) )
        blue_dds_pulses.append( (self.start + self.p.doppler_cooling_duration, self.p.doppler_cooling_frequency_397, -63.0) )
        red_dds_pulses.append(  (self.start, self.p.doppler_cooling_frequency_866, self.p.doppler_cooling_amplitude_866) )
        red_dds_pulses.append(  (self.start + self.p.doppler_cooling_duration, self.p.doppler_cooling_frequency_866, -63.0) )
        self.end = self.start + self.p.doppler_cooling_duration
        for pulses in [('110DP', blue_dds_pulses), ('866DP', red_dds_pulses)]:
            self.dds_pulses.append(pulses)

class CompositeSequence(SemaphoreSequence):
    
    def coniguration(self):
        return {}
    
    def sequence(self):
        self.addSequence(DopplerCooling)
        print self.dds_pulses

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    from labrad import types as T
    replace = {'doppler_cooling_duration':T.Value(1.0,'ms')}
    #dc = DopplerCooling(cxn.semaphore, **replace)
    cs = CompositeSequence(cxn.semaphore, **replace)