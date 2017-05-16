from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class local_rotation(pulse_sequence):
    
    required_parameters = [
                          ('LocalRotation','amplitude'),
                          ('LocalRotation','frequency'),
                          ('LocalRotation','pi_time'),
                          ('LocalRotation', 'sp_amplitude'),
                          ]

    def sequence(self):
        #this hack will be not needed with the new dds parsing methods
        pl = self.parameters.LocalRotation
        
        # choosing the frequency from the carrires dict
        freq_729=self.Calc_freq(pl.line_selection)
        
        
        frequency_advance_duration = WithUnit(6, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        
        time = pl.pi_time
        
        self.end = self.start + 2*frequency_advance_duration + time
        #first advance the frequency but keep amplitude low        
        self.addDDS('729local', self.start, frequency_advance_duration, freq_729 , ampl_off)
        #turn on
        self.addDDS('729local', self.start + frequency_advance_duration, time, freq_729, pl.amplitude)
        
        
        ## commented running the SP DDS from running from the pulser 
        
        #f = WithUnit(80.0 - 0.2, 'MHz')
        #amp = pl.sp_amplitude
        #self.addDDS('SP_local', self.start, frequency_advance_duration, f, ampl_off)
        #self.addDDS('SP_local', self.start + frequency_advance_duration, time, f, amp)
        
