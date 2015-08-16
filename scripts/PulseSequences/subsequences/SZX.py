from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit


class szx_ramsey(pulse_sequence):

    required_parameters = [
        ('SZX', 'frequency'),
        ('SZX', 'carrier_amplitude'),
        ('SZX', 'szx_amplitude'),
        ('SZX', 'szx_duration'),
        ('SZX', 'ramsey_pulse_duration'),
        ('SZX', 'second_pulse_phase'),
        ]

    def sequence(self):

        p = self.parameters.SZX
        frequency_advance_duration = WithUnit(6, 'us')
        buf = WithUnit(5., 'us') # a little extra time to account for TTL delays
        ampl_off = WithUnit(-63., 'dBm')

        car_amp = p.carrier_amplitude
        szx_amp = p.szx_amplitude
        p0 = WithUnit(0., 'deg')
        p2 = p.second_pulse_phase
        t_pi2 = p.ramsey_pulse_duration
        gate_duration = p.szx_duration

        # advance the dds frequency without pulsing anything on
        self.addDDS('729DP_1', self.start, frequency_advance_duration, p.frequency, ampl_off)
        
        # carrier pi/2 pulse
        self.addDDS('729DP_1', self.start + frequency_advance_duration, t_pi2, p.frequency, car_amp, p0)
        te = self.start + frequency_advance_duration + t_pi2 + buf
        
        # now bichromatic pulse
        self.addTTL('bichromatic_2', te, gate_duration + 2*buf)
        self.addDDS('729DP_1', te + buf, gate_duration, p.frequency, szx_amp, p0)
        te = te + gate_duration + 2*buf

        # second carrier pulse
        self.addDDS('729DP_1', te+buf, t_pi2, p.frequency, car_amp, p2)
        self.end = te + buf + t_pi2

class szx(pulse_sequence):

    required_parameters = [
        ('SZX', 'frequency'),
        ('SZX', 'szx_amplitude'),
        ('SZX', 'szx_duration'),
        ]

    def sequence(self):

        p = self.parameters.SZX
        frequency_advance_duration = WithUnit(6, 'us')
        buf = WithUnit(5, 'us') # a little extra time to account for TTL delays
        ampl_off = WithUnit(-63., 'dBm')

        szx_amp = p.szx_amplitude
        gate_duration = p.szx_duration
        
        self.addDDS('729', self.start, frequency_advance_duration, p.frequency, ampl_off)
        te = self.start + frequency_advance_duration
        self.addTTL('bichromatic_1', te, gate_duration + 2*buf)
        self.addDDS('729', te , gate_duration, p.frequency, szx_amp)
        self.end = te + gate_duration + buf
