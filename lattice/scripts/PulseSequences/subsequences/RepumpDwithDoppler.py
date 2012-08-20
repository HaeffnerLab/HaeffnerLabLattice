from scripts.PulseSequences.PulseSequence import PulseSequence
from RepumpD import repump_d
from DopplerCooling import doppler_cooling 

class doppler_cooling_after_repump_d(PulseSequence):
    
    @staticmethod
    def configuration():
        config = [
                  'doppler_cooling_duration',
                  ]
        return config
    
    @staticmethod
    def needs_subsequences():
        return [repump_d, doppler_cooling]
    
    def sequence(self):
        self.addSequence(repump_d)
        stop_repump_d = self.end
        self.addSequence(doppler_cooling, position = self.start, **{'doppler_cooling_duration': stop_repump_d + self.p.doppler_cooling_duration})