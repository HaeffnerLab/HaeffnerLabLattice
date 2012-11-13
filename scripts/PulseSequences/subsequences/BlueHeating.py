from lattice.scripts.PulseSequences.PulseSequence import PulseSequence
from lattice.scripts.PulseSequences.subsequences.DopplerCooling import doppler_cooling

class global_blue_heating(PulseSequence):
    
    def configuration(self):

        config = [
                'global_blue_heating_frequency_397', 
                'global_blue_heating_amplitude_397', 
                'blue_heating_frequency_866', 
                'blue_heating_amplitude_866', 
                'blue_heating_duration',
                ]
        return config
    
    def sequence(self):
        replace = {
                   'doppler_cooling_frequency_397':self.p.global_blue_heating_frequency_397,
                   'doppler_cooling_amplitude_397':self.p.global_blue_heating_amplitude_397,
                   'doppler_cooling_frequency_866':self.p.blue_heating_frequency_866,
                   'doppler_cooling_amplitude_866':self.p.blue_heating_amplitude_866,
                   'doppler_cooling_duration':self.p.blue_heating_duration,
                   }
        self.addSequence(doppler_cooling, **replace)

class local_blue_heating(PulseSequence):
    
    def configuration(self):
        
        config = [
                  'local_blue_heating_frequency_397', 
                  'local_blue_heating_amplitude_397', 
                  'blue_heating_frequency_866', 
                  'blue_heating_amplitude_866', 
                  'blue_heating_duration',
                  'doppler_cooling_repump_additional'
                  ]
        return config
    
    def sequence(self):
        
        dds = self.dds_pulses
        ttl = self.ttl_pulses
        repump_duration = self.p.blue_heating_duration + self.p.doppler_cooling_repump_additional
        dds.append( ('radial',self.start, self.p.blue_heating_duration, self.p.local_blue_heating_frequency_397, self.p.local_blue_heating_amplitude_397) )
        if self.p.blue_heating_duration.value > 40e-9:
            ttl.append( ('radial', self.start, self.p.blue_heating_duration))
        dds.append( ('866DP',self.start, repump_duration, self.p.blue_heating_frequency_866, self.p.blue_heating_amplitude_866) )
        self.end = self.start + repump_duration