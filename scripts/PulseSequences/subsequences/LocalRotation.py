from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class local_rotation(pulse_sequence):
    
    required_parameters = [
                          ('LocalRotation','amplitude'),
                          ('LocalRotation','frequency'),
                          ('LocalRotation','pi_time'),
                          ]

    def sequence(self):
        #this hack will be not needed with the new dds parsing methods
        pl = self.parameters.LocalRotation
        frequency_advance_duration = WithUnit(6, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        self.end = self.start + 2*frequency_advance_duration + pl.pi_time
        #first advance the frequency but keep amplitude low        
        self.addDDS('729DP_1', self.start, frequency_advance_duration, pl.frequency, ampl_off)
        #turn on
        self.addDDS('729DP_1', self.start + frequency_advance_duration, pl.pi_time, pl.frequency, pl.amplitude)
        
        # make sure the local pulse is off before starting the next thing
        self.addDDS('729DP_1', self.start, frequency_advance_duration, pl.frequency, ampl_off)

        f = WithUnit(80., 'MHz')
        amp = WithUnit(-12., 'dBm')
        self.addDDS('stark_shift', self.start, frequency_advance_duration, f, ampl_off)
        self.addDDS('stark_shift', self.start + frequency_advance_duration, pl.pi_time, f, amp)