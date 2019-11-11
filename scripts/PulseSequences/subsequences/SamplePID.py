from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class sample_pid(pulse_sequence):
    required_parameters = [ ('StatePreparation','PIDSampleTime')]
    
    def sequence(self):
        p = self.parameters.StatePreparation
        self.end = self.start + p.PIDSampleTime
        print self.end
        freq = WithUnit(220.0, 'MHz')
        amp = WithUnit(-5.0, 'dBm')
        dur = p.PIDSampleTime
        
        self.addDDS('854DP', self.start, dur, WithUnit(80.0, 'MHz'), amp)
        self.addDDS('729global', self.start, dur, freq, amp)
        #self.addDDS('729local', self.start, dur, freq, amp)
        #self.addTTL('sample729', self.start, dur - WithUnit(200.0, 'us')) # make sure we don't leave the pid sampling when the light is off