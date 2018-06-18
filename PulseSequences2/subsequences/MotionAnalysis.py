from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from treedict import TreeDict
#from OpticalPumping import optical_pumping
from labrad.units import WithUnit

class MotionAnalysis(pulse_sequence):
    '''
    Pulse sequence for reading out the state of the ion. 
    '''
   
    
    def sequence(self):
        ma = self.parameters.Motion_Analysis
        

        # need to update the frequect
        freq_397 = self.parameters.DopplerCooling.doppler_cooling_frequency_397  # WithUnit(85.0, 'MHz')
        # freq_866 = WithUnit(80.0, 'MHz')
        
        self.addTTL('397mod', self.start, ma.pulse_width_397 + WithUnit(2, 'us')) # 2 us for safe TTL switch on        
        self.addDDS('global397', self.start + WithUnit(1, 'us'), ma.pulse_width_397, freq_397, ma.amplitude_397)
        # self.addDDS('866DP', self.start + WithUnit(1, 'us'), ma.pulse_width_397, freq_866, ma.amplitude_866)
        self.addTTL('866DP', self.start + WithUnit(0.2, 'us'), ma.pulse_width_397+ WithUnit(0.1, 'us') )

        self.end = self.start + ma.pulse_width_397 + WithUnit(2, 'us')

        # start = self.start + ma.pulse_width_397 + WithUnit(2, 'us') + ma.ramsey_time
        
        # self.addTTL('397mod', start, ma.pulse_width_397 + WithUnit(2, 'us'))
        # self.addDDS('global397', start + WithUnit(1, 'us'), ma.pulse_width_397, freq_397, ma.amplitude_397)
        # self.addDDS('866DP', start + WithUnit(1, 'us'), ma.pulse_width_397, freq_866, ma.amplitude_866)        
        
        # self.end = start + ma.pulse_width_397 + WithUnit(2, 'us')
        
        #self.end = self.start + ma.pulse_width_397 + WithUnit(2, 'us')
        # print("dont forget to call optical pumping after this BEFROE a measurement")
        #self.addSequence(optical_pumping)
