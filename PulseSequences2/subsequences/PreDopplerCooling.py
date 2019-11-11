from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class PreDopplerCooling(pulse_sequence):
   
    #def addDDS(self, channel, start, duration, frequency, amplitude, phase = WithUnit(0, 'deg'), profile = 0):
    def sequence(self):
        p = self.parameters.DopplerCooling
        p_854 = self.parameters.RepumpD_5_2
        #print "Doppler Cooling" , p.doppler_cooling_duration
        
        
#         repump_duration = p.doppler_cooling_duration + p.doppler_cooling_repump_additional
        if (p.doppler_cooling_frequency_397 - WithUnit(15.0, "MHz") ) < WithUnit(50, "MHz"):
            pre_freq = WithUnit(50, "MHz")
        else:
            pre_freq = p.doppler_cooling_frequency_397 - WithUnit(15.0, "MHz")
        self.addDDS ('397',self.start, p.pre_duration, pre_freq, WithUnit(-12.0, 'dBm') )
        self.addDDS('854DP', self.start, p.pre_duration, p_854.repump_d_frequency_854, p_854.repump_d_amplitude_854)
        #self.addDDS ('866',self.start, repump_duration, p.doppler_cooling_frequency_866, p.doppler_cooling_amplitude_866)
        # changing the 866 from a dds to a rf source enabled by a switch
        self.addTTL('866DP', self.start + WithUnit(0.2, 'us'), p.pre_duration- WithUnit(0.1, 'us') )
        self.end = self.start + p.pre_duration
        
