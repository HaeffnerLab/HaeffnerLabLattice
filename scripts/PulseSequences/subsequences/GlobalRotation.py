from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
import numpy as np
from labrad.units import WithUnit

class global_rotation(pulse_sequence):
    
    required_parameters = [
                          ('GlobalRotation','amplitude'),
                          ('GlobalRotation','frequency'),
                          ('GlobalRotation','pi_time'),
                          ('GlobalRotation','angle'),
                          ('GlobalRotation','phase'),
                          ]

    def sequence(self):
        #this hack will be not needed with the new dds parsing methods
        p = self.parameters.GlobalRotation
        frequency_advance_duration = WithUnit(6, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        rotation_fraction = p.angle['rad']/np.pi
        time = p.pi_time*rotation_fraction
        self.end = self.start + frequency_advance_duration + time
        #first advance the frequency but keep amplitude low        
        self.addDDS('729global', self.start, frequency_advance_duration, p.frequency, ampl_off)
        #turn on
        self.addDDS('729global', self.start + frequency_advance_duration, time, p.frequency, p.amplitude, p.phase)