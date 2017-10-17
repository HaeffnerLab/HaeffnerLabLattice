from common.devel.bum.sequences.pulse_sequence import pulse_sequence
import numpy as np
from labrad.units import WithUnit

class Rotation(pulse_sequence):
    
    '''
     729 rotation with controlled phase and angle 
    '''

    def sequence(self):
        #this hack will be not needed with the new dds parsing methods
        p = self.parameters.Rotation
        frequency_advance_duration = WithUnit(6, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        
       
        rotation_fraction = p.angle['rad']/np.pi
        #rotation_fraction = 0.5
        time = p.pi_time*rotation_fraction
        
        print "454545"
        print "rotating ", p.channel_729 , " at frequency ", p.frequency
        print "rotation duration ", time , " at amplitude  ", p.amplitude
        print " phase " , p.phase
        
        self.end = self.start + frequency_advance_duration + time
        #first advance the frequency but keep amplitude low        
        self.addDDS( p.channel_729, self.start, frequency_advance_duration, p.frequency, ampl_off)
        #turn on
        self.addDDS( p.channel_729, self.start + frequency_advance_duration, time, p.frequency, p.amplitude, p.phase)