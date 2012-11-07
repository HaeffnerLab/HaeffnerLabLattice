from scripts.PulseSequences.PulseSequence import PulseSequence
from scripts.PulseSequences.subsequences.DopplerCooling import doppler_cooling

class global_blue_heating(PulseSequence):
    
    def configuration(self):
        config = [
                'global_blue_heating_frequency_397', 
                'global_blue_heating_amplitude_397', 
                'global_blue_heating_frequency_866', 
                'global_blue_heating_amplitude_866', 
                'global_blue_heating_duration',
                ]
        return config
    
    def sequence(self):
        
        replace = {
                   'doppler_cooling_frequency_397':self.p.global_blue_heating_frequency_397,
                   'doppler_cooling_amplitude_397':self.p.global_blue_heating_amplitude_397,
                   'doppler_cooling_frequency_866':self.p.global_blue_heating_frequency_866,
                   'doppler_cooling_amplitude_866':self.p.global_blue_heating_amplitude_866,
                   'doppler_cooling_duration':self.p.global_blue_heating_duration,
                   }
        self.addSequence(doppler_cooling, **replace)
        
#        pulses = self.dds_pulses
#        pulses.append( ('110DP',self.start, T.Value(150,'us'), self.p.global_blue_heating_frequency_397, self.p.global_blue_heating_amplitude_397) )
#        pulses.append( ('866DP',self.start, T.Value(300,'us'), self.p.global_blue_heating_frequency_866, self.p.global_blue_heating_amplitude_866) )
#        self.end = self.start +  T.Value(300,'us')# + repump_duration