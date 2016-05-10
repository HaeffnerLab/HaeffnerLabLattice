from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class molmer_sorensen(pulse_sequence):
    
    required_parameters = [
                          ('MolmerSorensen','frequency'),
                          ('MolmerSorensen','amplitude'),
                          ('MolmerSorensen','duration'),
                          ('MolmerSorensen','phase'),
                          ('MolmerSorensen','analysis_pulse_enable'),
                          ('MolmerSorensen','analysis_phase'),
                          ('MolmerSorensen','analysis_amplitude'),
                          ('MolmerSorensen','analysis_duration'),
                          ('MolmerSorensen','shape_profile'),

                          ('LocalStarkShift', 'enable'),
                          ('LocalStarkShift','amplitude'),
                          ('LocalStarkShift', 'detuning'), # detuning from the carrier transition
                          ]

    def sequence(self):
        #this hack will be not needed with the new dds parsing methods
        slope_dict = {0:0.0, 2:2.0, 4:5.0, 6:600.0}
        p = self.parameters.MolmerSorensen
        pl = self.parameters.LocalStarkShift
        frequency_advance_duration = WithUnit(6, 'us')
        try:
            slope_duration = WithUnit(int(slope_dict[p.shape_profile]),'us')
        except KeyError:
            raise Exception('Cannot find shape profile: ' + str(p.shape_profile))
        ampl_off = WithUnit(-63.0, 'dBm')
        self.end = self.start + 2*frequency_advance_duration + p.duration + slope_duration
        #first advance the frequency but keep amplitude low
        self.addDDS('729global', self.start, frequency_advance_duration, p.frequency, ampl_off)
        self.addDDS('729global', self.start + frequency_advance_duration, p.duration, p.frequency, p.amplitude, p.phase, profile=int(p.shape_profile))
        self.addTTL('bichromatic_1', self.start, p.duration + 2*frequency_advance_duration + slope_duration)
        
        if pl.enable: # add a stark shift on the localized beam
            f = WithUnit(80. - 0.2, 'MHz') + pl.detuning
            amp = WithUnit(-10., 'dBm')
            print p.frequency
            self.addDDS('SP_local', self.start, frequency_advance_duration, f, ampl_off)
            self.addDDS('SP_local', self.start + frequency_advance_duration, p.duration, f, pl.amplitude, profile=int(p.shape_profile))
            
            # turn on the double pass at -15 dBm for the stark shift
            self.addDDS('729local', self.start, frequency_advance_duration, p.frequency, ampl_off)
            self.addDDS('729local', self.start + frequency_advance_duration, p.duration, p.frequency, amp, p.phase, profile=int(p.shape_profile))
            
        self.addDDS('729global', self.start + p.duration + 2*frequency_advance_duration + slope_duration, frequency_advance_duration, p.frequency, ampl_off)
        self.addDDS('729local', self.start + p.duration + 2*frequency_advance_duration + slope_duration, frequency_advance_duration, p.frequency, ampl_off)
        
        self.end = self.end + frequency_advance_duration