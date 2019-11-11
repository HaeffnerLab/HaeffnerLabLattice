from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit
import numpy as np

class LocalRotation(pulse_sequence):
    
    required_parameters = [
                          ('LocalRotation','amplitude'),
                          ('LocalRotation','frequency'),
                          ('LocalRotation','pi_time'),
                          ('LocalRotation', 'sp_amplitude'),
                          ]

    def sequence(self):
        #this hack will be not needed with the new dds parsing methods
        p = self.parameters.LocalRotation
        
        
      
        
        frequency_advance_duration = WithUnit(6, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        
        #rotation_fraction = 0.5
        rotation_fraction = p.angle['rad']/np.pi
        time = p.pi_time*rotation_fraction
        freq_729= p.frequency
        print "Local Rotation"
        print "freq_729" ,freq_729
        print "time",time
        
        self.end = self.start + 2*frequency_advance_duration + time
        #first advance the frequency but keep amplitude low        
        self.addDDS('729local', self.start, frequency_advance_duration, freq_729 , ampl_off)
        #turn on
        self.addDDS('729local', self.start + frequency_advance_duration, time, freq_729, p.amplitude, p.phase)
        
        
        ## commented running the SP DDS from running from the pulser 
        
        #f = WithUnit(80.0 - 0.2, 'MHz')
        #amp = pl.sp_amplitude
        #self.addDDS('SP_local', self.start, frequency_advance_duration, f, ampl_off)
        #self.addDDS('SP_local', self.start + frequency_advance_duration, time, f, amp)
       
    
    