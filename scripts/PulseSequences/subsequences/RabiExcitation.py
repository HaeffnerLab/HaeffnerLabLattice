from lattice.scripts.PulseSequences.PulseSequence import PulseSequence
from labrad.units import WithUnit

class rabi_excitation(PulseSequence):
    
    def configuration(self):
        config = [
                  'rabi_excitation_frequency',
                  'rabi_excitation_amplitude',
                  'rabi_excitation_duration',
                  ]
        return config
    
    
    def sequence(self):
        #this hack will be not needed with the new dds parsing methods
        frequency_advance_duration = WithUnit(5, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        self.end = self.start + frequency_advance_duration + self.p.rabi_excitation_duration
        #first advance the frequency but keep amplitude low        
        self.dds_pulses.append(('729DP', self.start, frequency_advance_duration, self.p.rabi_excitation_frequency, ampl_off))
        #turn on
        self.dds_pulses.append(('729DP', self.start + frequency_advance_duration, self.p.rabi_excitation_duration, self.p.rabi_excitation_frequency, self.p.rabi_excitation_amplitude))