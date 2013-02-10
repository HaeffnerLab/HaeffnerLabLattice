from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from OpticalPumpingContinuous import optical_pumping_continuous
from OpticalPumpingPulsed import optical_pumping_pulsed

class optical_pumping(pulse_sequence):
    
    
    required_parameters = [
                  'optical_pumping_continuous',
                  'optical_pumping_pulsed',
                  'optical_pumping_frequency_729',
                  'optical_pumping_frequency_854',
                  'optical_pumping_frequency_866',
                  'optical_pumping_amplitude_729',
                  'optical_pumping_amplitude_854',
                  'optical_pumping_amplitude_866'
                  ]
    
    required_subsequences = [optical_pumping_continuous, optical_pumping_pulsed]
    
    def sequence(self):
        if (self.optical_pumping_continuous == self.optical_pumping_pulsed):
            raise Exception("Incorrectly Selected Optical Pumping Type") 
        if self.optical_pumping_continuous:
            replace = {
                       'optical_pumping_continuous_frequency_854':self.optical_pumping_frequency_854,
                       'optical_pumping_continuous_amplitude_854':self.optical_pumping_amplitude_854,
                       'optical_pumping_continuous_frequency_729':self.optical_pumping_frequency_729,
                       'optical_pumping_continuous_amplitude_729':self.optical_pumping_amplitude_729,
                       'optical_pumping_continuous_frequency_866':self.optical_pumping_frequency_866,
                       'optical_pumping_continuous_amplitude_866':self.optical_pumping_amplitude_866,
                       }
            self.addSequence(optical_pumping_continuous, **replace)
        elif self.optical_pumping_pulsed:
            replace = {
                       'optical_pumping_pulsed_frequency_854':self.optical_pumping_frequency_854,
                       'optical_pumping_pulsed_amplitude_854':self.optical_pumping_amplitude_854,
                       'optical_pumping_pulsed_frequency_729':self.optical_pumping_frequency_729,
                       'optical_pumping_pulsed_amplitude_729':self.optical_pumping_amplitude_729,
                       'optical_pumping_pulsed_frequency_866':self.optical_pumping_frequency_866,
                       'optical_pumping_pulsed_amplitude_866':self.optical_pumping_amplitude_866,
                       }
            self.addSequence(optical_pumping_pulsed, **replace)