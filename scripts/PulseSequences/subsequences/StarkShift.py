from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class stark_shift_global(pulse_sequence):

    required_parameters = [
        ('StarkShiftGlobal', 'frequency'),
        ('StarkShiftGlobal', 'amplitude'),
        ('StarkShiftGlobal', 'duration'),
        ]

    def sequence(self):
        p = self.parameters.StarkShiftGlobal
        slope_duration = WithUnit(5.0, 'us')
        frequency_advance_duration = WithUnit(6, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        
        self.end = self.start + p.duration + slope_duration + frequency_advance_duration
        
        self.addDDS('729global', self.start, frequency_advance_duration, p.frequency, ampl_off)
        self.addDDS('729global', self.start + frequency_advance_duration , p.duration, p.frequency, p.amplitude, profile = 4)