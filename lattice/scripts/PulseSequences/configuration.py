class DopplerCoolingConfig(object):
    
    params = {
                'doppler_cooling_frequency_397' : ['doppler_cooling_frequency_397'],
                'doppler_cooling_amplitude_397' : ['doppler_cooling_amplitude_397'],
                'doppler_cooling_frequency_866' : ['doppler_cooling_frequency_866'],
                'doppler_cooling_amplitude_866' : ['doppler_cooling_amplitude_866'],
                'doppler_cooling_duration' : ['doppler_cooling_duration']
              }

class RabiExcitationConfig(object):
    
    params = {
              'rabi_excitation_time' : ['729Experiments','Spectrum','excitation_time'],
              'rabi_excitation_frequency': ['729Experiments','RabiFlopping','frequency']
              'rabi_excitation_amplitude': ['729Experiments','amplitude_729']
              }