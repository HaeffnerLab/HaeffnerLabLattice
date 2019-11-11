from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class szx(pulse_sequence):

    required_parameters = [
        ('SZX', 'frequency'),
        ('SZX', 'amplitude'),
        ('SZX', 'duration'),
        ]

    def sequence(self):

        p = self.parameters.SZX
        frequency_advance_duration = WithUnit(6, 'us')
        buf = WithUnit(5, 'us') # a little extra time to account for TTL delays
        ampl_off = WithUnit(-63., 'dBm')

        szx_amp = p.amplitude
        gate_duration = p.duration
        
        self.addDDS('729local', self.start, frequency_advance_duration, p.frequency, ampl_off)
        
        te = self.start + frequency_advance_duration
        self.addTTL('bichromatic_2', te, gate_duration + 2*buf)
        self.addDDS('729local', te + buf , gate_duration, p.frequency, szx_amp, profile = 4)
        self.addDDS('SP_local', te + buf , gate_duration, WithUnit(79.3, 'MHz'), ampl_off) # move it off resonance
        self.end = te + gate_duration + 2*buf
