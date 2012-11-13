from lattice.scripts.PulseSequences.PulseSequence import PulseSequence
from OpticalPumpingContinuous import optical_pumping_continuous
from OpticalPumpingPulsed import optical_pumping_pulsed

class optical_pumping(PulseSequence):
    
    def configuration(self):
        config = [
                  'optical_pumping_continuous',
                  'optical_pumping_pulsed',
                  'optical_pumping_frequency_729',
                  'optical_pumping_frequency_854',
                  'optical_pumping_frequency_866',
                  'optical_pumping_amplitude_729',
                  'optical_pumping_amplitude_854',
                  'optical_pumping_amplitude_866'
                  ]
        return config
    
    def sequence(self):
        if (self.p.optical_pumping_continuous == self.p.optical_pumping_pulsed):
            raise Exception("Incorrectly Selected Optical Pumping Type") 
        if self.p.optical_pumping_continuous:
            replace = {
                       'optical_pumping_continuous_frequency_854':self.p.optical_pumping_frequency_854,
                       'optical_pumping_continuous_amplitude_854':self.p.optical_pumping_amplitude_854,
                       'optical_pumping_continuous_frequency_729':self.p.optical_pumping_frequency_729,
                       'optical_pumping_continuous_amplitude_729':self.p.optical_pumping_amplitude_729,
                       'optical_pumping_continuous_frequency_866':self.p.optical_pumping_frequency_866,
                       'optical_pumping_continuous_amplitude_866':self.p.optical_pumping_amplitude_866,
                       }
            self.addSequence(optical_pumping_continuous, **replace)
        elif self.p.optical_pumping_pulsed:
            replace = {
                       'optical_pumping_pulsed_frequency_854':self.p.optical_pumping_frequency_854,
                       'optical_pumping_pulsed_amplitude_854':self.p.optical_pumping_amplitude_854,
                       'optical_pumping_pulsed_frequency_729':self.p.optical_pumping_frequency_729,
                       'optical_pumping_pulsed_amplitude_729':self.p.optical_pumping_amplitude_729,
                       'optical_pumping_pulsed_frequency_866':self.p.optical_pumping_frequency_866,
                       'optical_pumping_pulsed_amplitude_866':self.p.optical_pumping_amplitude_866,
                       }
            self.addSequence(optical_pumping_pulsed, **replace)