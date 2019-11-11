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
        frequency_advance_duration = WithUnit(6, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        
        time = pl.pi_time
        self.end = self.start + 2*frequency_advance_duration + time
        #first advance the frequency but keep amplitude low        
        self.addDDS('729local', self.start, frequency_advance_duration, pl.frequency, ampl_off)
        #turn on
        self.addDDS('729local', self.start + frequency_advance_duration, time, pl.frequency, pl.amplitude)
        
        # make sure the local pulse is off before starting the next thing
        #self.addDDS('729local', self.start + frequency_advance_duration+time, frequency_advance_duration, pl.frequency, ampl_off)

        f = WithUnit(80.0 - 0.2, 'MHz')
        amp = pl.sp_amplitude
        self.addDDS('SP_local', self.start, frequency_advance_duration, f, ampl_off)
        self.addDDS('SP_local', self.start + frequency_advance_duration, time, f, amp)
        
class local_pi_over_2(pulse_sequence):
    
    required_parameters = [
                          ('LocalRotation','amplitude'),
                          ('LocalRotation','frequency'),
                          ('LocalRotation','pi_time'),
                          ('LocalRotation', 'sp_amplitude'),
                          ('LocalRotation', 'phase'),
                          ]

    def sequence(self):
        #this hack will be not needed with the new dds parsing methods
        pl = self.parameters.LocalRotation
        frequency_advance_duration = WithUnit(6, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        
        time = pl.pi_time/2.
        self.end = self.start + 2*frequency_advance_duration + time
        #first advance the frequency but keep amplitude low        
        self.addDDS('729local', self.start, frequency_advance_duration, pl.frequency, ampl_off)
        #turn on
        self.addDDS('729local', self.start + frequency_advance_duration, time, pl.frequency, pl.amplitude, pl.phase)
        
        # make sure the local pulse is off before starting the next thing
        self.addDDS('729local', self.start, frequency_advance_duration, pl.frequency, ampl_off)

        f = WithUnit(80.0 - 0.2, 'MHz')
        amp = pl.sp_amplitude
        self.addDDS('SP_local', self.start, frequency_advance_duration, f, ampl_off)
        self.addDDS('SP_local', self.start + frequency_advance_duration, time, f, amp)
        
class local_pi_over_2_no_splocal(pulse_sequence):
    
    required_parameters = [
                          ('LocalRotation','amplitude'),
                          ('LocalRotation','frequency'),
                          ('LocalRotation','pi_time'),
                          ('LocalRotation', 'phase'),
                          ]

    def sequence(self):
        # use this if you don't want to use sp_local to drive the single pass
        pl = self.parameters.LocalRotation
        frequency_advance_duration = WithUnit(6, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        
        time = pl.pi_time/2.
        self.end = self.start + 2*frequency_advance_duration + time
        #first advance the frequency but keep amplitude low        
        self.addDDS('729local', self.start, frequency_advance_duration, pl.frequency, ampl_off)
        #turn on
        self.addDDS('729local', self.start + frequency_advance_duration, time, pl.frequency, pl.amplitude, pl.phase)
        print pl.phase
        # make sure the local pulse is off before starting the next thing
        self.addDDS('729local', self.start, frequency_advance_duration, pl.frequency, ampl_off)