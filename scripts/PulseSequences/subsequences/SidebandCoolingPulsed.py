from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from OpticalPumpingPulsed import optical_pumping_pulsed

class sideband_cooling_pulsed(pulse_sequence):
    
    required_parameters = [
                           'sideband_cooling_pulsed_cycles',
                           'sideband_cooling_pulsed_duration_729',
                           'sideband_cooling_pulsed_duration_repumps',
                           'sideband_cooling_pulsed_duration_additional_866',
                           'sideband_cooling_pulsed_duration_between_pulses',
                           'sideband_cooling_pulsed_frequency_854',
                           'sideband_cooling_pulsed_amplitude_854',
                           'sideband_cooling_pulsed_frequency_729',
                           'sideband_cooling_pulsed_amplitude_729',
                           'sideband_cooling_pulsed_frequency_866',
                           'sideband_cooling_pulsed_amplitude_866',
                           ]
    
    required_subsequences = [optical_pumping_pulsed]
    
    def sequence(self):
        replace = self.make_replace()
        self.addSequence(optical_pumping_pulsed, **replace)
    
    def make_replace(self):
        replace = {
                   'optical_pumping_pulsed_cycles':self.sideband_cooling_pulsed_cycles,
                   'optical_pumping_pulsed_duration_729': self.sideband_cooling_pulsed_duration_729,
                   'optical_pumping_pulsed_duration_repumps': self.sideband_cooling_pulsed_duration_repumps,
                   'optical_pumping_pulsed_duration_additional_866': self.sideband_cooling_pulsed_duration_additional_866,
                   'optical_pumping_pulsed_duration_between_pulses': self.sideband_cooling_pulsed_duration_between_pulses,
                   'optical_pumping_pulsed_frequency_854':self.sideband_cooling_pulsed_frequency_854,
                   'optical_pumping_pulsed_amplitude_854':self.sideband_cooling_pulsed_amplitude_854,
                   'optical_pumping_pulsed_frequency_729':self.sideband_cooling_pulsed_frequency_729,
                   'optical_pumping_pulsed_amplitude_729':self.sideband_cooling_pulsed_amplitude_729,
                   'optical_pumping_pulsed_frequency_866':self.sideband_cooling_pulsed_frequency_866,
                   'optical_pumping_pulsed_amplitude_866':self.sideband_cooling_pulsed_amplitude_866,
                  }
        return replace