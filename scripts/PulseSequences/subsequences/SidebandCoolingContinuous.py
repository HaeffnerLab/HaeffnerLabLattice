from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from OpticalPumpingContinuous import optical_pumping_continuous

class sideband_cooling_continuous(pulse_sequence):

    required_parameters = [
                           'sideband_cooling_continuous_duration',
                           'sideband_cooling_continuous_frequency_854',
                           'sideband_cooling_conitnuous_amplitude_854',
                           'sideband_cooling_continuous_frequency_729',
                           'sideband_cooling_continuous_amplitude_729',
                           'sideband_cooling_continuous_frequency_866',
                           'sideband_cooling_continuous_amplitude_866',
                           ]
    
    required_subsequences = [optical_pumping_continuous]
    
    def sequence(self):
        replace = self.make_replace()
        self.addSequence(optical_pumping_continuous, **replace)

    def make_replace(self):
        replace = {
                   'optical_pumping_continuous_duration': self.sideband_cooling_continuous_duration,
                   'optical_pumping_continuous_frequency_854':self.sideband_cooling_continuous_frequency_854,
                   'optical_pumping_continuous_amplitude_854':self.sideband_cooling_conitnuous_amplitude_854,
                   'optical_pumping_continuous_frequency_729':self.sideband_cooling_continuous_frequency_729,
                   'optical_pumping_continuous_amplitude_729':self.sideband_cooling_continuous_amplitude_729,
                   'optical_pumping_continuous_frequency_866':self.sideband_cooling_continuous_frequency_866, 
                   'optical_pumping_continuous_amplitude_866':self.sideband_cooling_continuous_amplitude_866,
                   }
        return replace