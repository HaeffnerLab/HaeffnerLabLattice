from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from treedict import TreeDict
from OpticalPumping import optical_pumping
from labrad.units import WithUnit

class motion_analysis(pulse_sequence):
    '''
    Pulse sequence for reading out the state of the ion. 
    '''
    required_parameters = [
                           ('Motion_Analysis','amplitude_397'),
                           ('Motion_Analysis','amplitude_866'),
                           ('Motion_Analysis','pulse_width_397'),
                           ('Motion_Analysis','ramsey_time')                           
                           ]
    required_subsequences = [optical_pumping]
    def sequence(self):
        ma = self.parameters.Motion_Analysis
        
        freq_397 = WithUnit(85.0, 'MHz')
        freq_866 = WithUnit(80.0, 'MHz')
        
        self.addTTL('397mod', self.start, ma.pulse_width_397 + WithUnit(2, 'us')) # 2 us for safe TTL switch on        
        self.addDDS('global397', self.start + WithUnit(1, 'us'), ma.pulse_width_397, freq_397, ma.amplitude_397)
        self.addDDS('866DP', self.start + WithUnit(1, 'us'), ma.pulse_width_397, freq_866, ma.amplitude_866)

        start = self.start + ma.pulse_width_397 + WithUnit(2, 'us') + ma.ramsey_time
        
        self.addTTL('397mod', start, ma.pulse_width_397 + WithUnit(2, 'us'))
        self.addDDS('global397', start + WithUnit(1, 'us'), ma.pulse_width_397, freq_397, ma.amplitude_397)
        self.addDDS('866DP', start + WithUnit(1, 'us'), ma.pulse_width_397, freq_866, ma.amplitude_866)        
        
        self.end = start + ma.pulse_width_397 + WithUnit(2, 'us')
        
        #self.end = self.start + ma.pulse_width_397 + WithUnit(2, 'us')
        self.addSequence(optical_pumping)
