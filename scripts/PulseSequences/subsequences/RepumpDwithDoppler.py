from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from RepumpD import repump_d
from DopplerCooling import doppler_cooling 

class doppler_cooling_after_repump_d(pulse_sequence):
    
    @classmethod
    def required_parameters(cls):
        return [ 'doppler_cooling_duration']
    
    @classmethod
    def required_subsequences(cls):
        return [repump_d, doppler_cooling]
    
    def sequence(self):
        self.addSequence(repump_d)
        stop_repump_d = self.end
        self.addSequence(doppler_cooling, position = self.start, **{'doppler_cooling_duration': stop_repump_d + self.doppler_cooling_duration})