from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class vaet(pulse_sequence):

    required_parameters = [
        ('VAET', 'frequency'),
        ('VAET', 'duration'),
        ('VAET', 'shape_profile'),

        ('MolmerSorensen', 'amplitude'),
        ('SZX', 'amplitude'),

        ('LocalStarkShift', 'enable'),
        ('LocalStarkShift','amplitude'),
        ('LocalStarkShift', 'detuning'), # detuning from the carrier transition
        ]
    
    def sequence(self):
        #this hack will be not needed with the new dds parsing methods
        slope_dict = {0:0.0, 2:2.0, 4:5.0, 6:600.0}
        ms = self.parameters.MolmerSorensen
        v = self.parameters.VAET
        szx = self.parameters.SZX
        pl = self.parameters.LocalStarkShift
        frequency_advance_duration = WithUnit(6, 'us')
        try:
            slope_duration = WithUnit(int(slope_dict[v.shape_profile]),'us')
        except KeyError:
            raise Exception('Cannot find shape profile: ' + str(v.shape_profile))
        ampl_off = WithUnit(-63.0, 'dBm')
        self.end = self.start + 2*frequency_advance_duration + v.duration + slope_duration
        #first advance the frequency but keep amplitude low
        self.addDDS('729global', self.start, frequency_advance_duration, v.frequency, ampl_off)
        self.addDDS('729local', self.start, frequency_advance_duration, v.frequency, ampl_off)
        # turn on bichro on the global and local beams at the same time
        self.addDDS('729global', self.start + frequency_advance_duration, v.duration, v.frequency, ms.amplitude, profile=int(v.shape_profile))
        self.addDDS('729local', self.start + frequency_advance_duration, v.duration, v.frequency, szx.amplitude, profile=int(v.shape_profile))
        #self.addDDS('729local', self.start + frequency_advance_duration, v.duration + slope_duration, v.frequency, szx.amplitude, profile=4)
        self.addTTL('bichromatic_1', self.start, v.duration + 2*frequency_advance_duration + slope_duration)
        self.addTTL('bichromatic_2', self.start, v.duration + 2*frequency_advance_duration + slope_duration)
        
        if pl.enable: # add a stark shift on the localized beam
            f = WithUnit(80. - 0.2, 'MHz') + pl.detuning
            #f = WithUnit(80.0 - 0.2, 'MHz') + pl.detuning
            self.addDDS('SP_local', self.start, frequency_advance_duration, f, ampl_off)
            self.addDDS('SP_local', self.start + frequency_advance_duration, v.duration, f, pl.amplitude, profile=int(v.shape_profile))
            #self.addDDS('SP_local', self.start + frequency_advance_duration, v.duration + slope_duration, f, pl.amplitude, profile=4)
            self.addDDS('SP_local', self.start + frequency_advance_duration + v.duration + slope_duration, frequency_advance_duration, f, ampl_off)

        self.addDDS('729global', self.start + frequency_advance_duration + v.duration + slope_duration, frequency_advance_duration, v.frequency, ampl_off)
        self.addDDS('729local', self.start + frequency_advance_duration + v.duration + slope_duration, frequency_advance_duration, v.frequency, ampl_off)
        
        
