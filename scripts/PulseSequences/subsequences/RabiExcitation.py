from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class rabi_excitation(pulse_sequence):
    
    required_parameters = [
                          'rabi_excitation_frequency',
                          'rabi_excitation_amplitude',
                          'rabi_excitation_duration',
                          ]

    def sequence(self):
        #this hack will be not needed with the new dds parsing methods
        frequency_advance_duration = WithUnit(6, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        self.end = self.start + frequency_advance_duration + self.rabi_excitation_duration
        #first advance the frequency but keep amplitude low        
        self.dds_pulses.append(('729DP', self.start, frequency_advance_duration, self.rabi_excitation_frequency, ampl_off))
        #turn on
        self.dds_pulses.append(('729DP', self.start + frequency_advance_duration, self.rabi_excitation_duration, self.rabi_excitation_frequency, self.rabi_excitation_amplitude))
        
class rabi_excitation_no_offset(pulse_sequence):
    
    required_parameters = [
                          'rabi_excitation_frequency',
                          'rabi_excitation_amplitude',
                          'rabi_excitation_duration',
                          ]
    
    def sequence(self):
        self.end = self.start + self.rabi_excitation_duration
        self.dds_pulses.append(('729DP', self.start, self.rabi_excitation_duration, self.rabi_excitation_frequency, self.rabi_excitation_amplitude))