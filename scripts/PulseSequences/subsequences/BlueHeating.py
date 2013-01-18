from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from lattice.scripts.PulseSequences.subsequences.DopplerCooling import doppler_cooling

class global_blue_heating(pulse_sequence):
    
    @classmethod
    def required_parameters(cls):
        config = [
                'global_blue_heating_frequency_397', 
                'global_blue_heating_amplitude_397', 
                'blue_heating_frequency_866', 
                'blue_heating_amplitude_866', 
                'blue_heating_duration',
                'blue_heating_repump_additional'
                ]
        return config
    
    @classmethod
    def required_subsequences(cls):
        return [doppler_cooling]
    
    def sequence(self):
        replace = {
                   'doppler_cooling_frequency_397':self.global_blue_heating_frequency_397,
                   'doppler_cooling_amplitude_397':self.global_blue_heating_amplitude_397,
                   'doppler_cooling_frequency_866':self.blue_heating_frequency_866,
                   'doppler_cooling_amplitude_866':self.blue_heating_amplitude_866,
                   'doppler_cooling_duration':self.blue_heating_duration,
                   'doppler_cooling_repump_additional':self.blue_heating_repump_additional
                   }
        self.addSequence(doppler_cooling, **replace)

class local_blue_heating(pulse_sequence):
    
    @classmethod
    def required_parameters(cls):
        
        config = [
                  'local_blue_heating_frequency_397', 
                  'local_blue_heating_amplitude_397', 
                  'blue_heating_frequency_866', 
                  'blue_heating_amplitude_866', 
                  'blue_heating_duration',
                  'blue_heating_repump_additional'
                  ]
        return config
    
    @classmethod
    def required_subsequences(cls):
        return [doppler_cooling]
    
    def sequence(self):
        
        dds = self.dds_pulses
        ttl = self.ttl_pulses
        repump_duration = self.blue_heating_duration + self.blue_heating_repump_additional
        dds.append( ('radial',self.start, self.blue_heating_duration, self.local_blue_heating_frequency_397, self.local_blue_heating_amplitude_397) )
        if self.blue_heating_duration.value > 40e-9:
            ttl.append( ('radial', self.start, self.blue_heating_duration))
        dds.append( ('866DP',self.start, repump_duration, self.blue_heating_frequency_866, self.blue_heating_amplitude_866) )
        self.end = self.start + repump_duration