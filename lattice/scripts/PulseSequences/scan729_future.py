from subsequences.DopplerCooling import doppler_cooling
from subsequences.EmptySequence import EmptySequence
from PulseSequence import PulseSequence
from labrad import types as T

class CompositeSequence(PulseSequence):
    
    def coniguration(self):
        return {}
    
    def sequence(self):
        print self.start, self.end
        self.addSequence(doppler_cooling)
        print self.start, self.end
        self.addSequence(EmptySequence, **{'duration': T.Value(10.0, 'us')})
        print self.start, self.end
        self.addSequence(doppler_cooling, position = T.Value(10, 's'))
        print self.start, self.end
        print self.dds_pulses


if __name__ == '__main__':
    replace = {
               'doppler_cooling_frequency_397':T.Value(110, 'MHz'),
               'doppler_cooling_amplitude_397':T.Value(-11, 'dBm'),
               'doppler_cooling_frequency_866':T.Value(80.0, 'MHz'),
               'doppler_cooling_amplitude_866':T.Value(-11, 'dBm'),
               'doppler_cooling_duration':T.Value(1.0,'ms')}
    cs = CompositeSequence(**replace)