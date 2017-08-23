from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

  
class RabiExcitation(pulse_sequence):
    '''
    Runs a 729 excitation with the Excitation_729 params
    '''

    def sequence(self):
        
        freq_729 = self.parameters.Excitation_729.rabi_excitation_frequency
        
        print "this is the 729 freq{}".format(freq_729)

        ampl_off = WithUnit(-63.0, 'dBm')
        frequency_advance_duration = WithUnit(6, 'us')
        
        duration_729 = self.parameters.Excitation_729.rabi_excitation_duration
        phase_729 = self.parameters.Excitation_729.rabi_excitation_phase
        amp_729 = self.parameters.Excitation_729.rabi_excitation_amplitude
        channel_729 = self.parameters.Excitation_729.channel_729
        #detuning = self.parameters.Excitation_729.detuning
        #freq_729 = freq_729 + detuning
        
        #first advance the frequency but keep amplitude low        
        self.addDDS(channel_729, self.start, frequency_advance_duration, freq_729, ampl_off)
        self.addDDS(channel_729, self.start + frequency_advance_duration, duration_729, freq_729, amp_729, phase_729)
        
        
        self.end = self.start + frequency_advance_duration + duration_729