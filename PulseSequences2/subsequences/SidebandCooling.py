from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
#from OpticalPumpingContinuous import optical_pumping_continuous
#from treedict import TreeDict

class sideband_cooling(pulse_sequence):
    '''
    Single step of side band cooling DOES NOT include the optical pumping usually required
    paramters:
    duration
    729- choose carrier transition and sideband
    729- channel, amp, ac stark shift
    854- freq, amp
    866- freq, amp
    '''
    
    def sequence(self):
        
        sc = self.parameters.SidebandCooling
                      
        freq_729 = self.Calc_freq(sc.line_selection,sc.sideband_selection, -1)+ sc.stark_shift
        channel_729 = self.parameters.SidebandCooling.channel_729
        
        repump_additional = self.parameters.OpticalPumpingContinuous.optical_pumping_continuous_repump_additional # need this for the additional repumper times
        
        #Setting times
        duration=self.parameters.SidebandCoolingContinuous.sideband_cooling_continuous_duration
        repump_dur_854 = duration+ repump_additional
        repump_dur_866 = duration + 2 * repump_additional
        
                
     
        self.addDDS(channel_729, self.start, duration, freq_729 , sc.sideband_cooling_amplitude_729)
        self.addDDS('854',       self.start, repump_dur_854, sc.sideband_cooling_frequency_854 , sc.sideband_cooling_amplitude_854)
        self.addDDS('866',       self.start, repump_dur_866, sc.sideband_cooling_frequency_866 , sc.sideband_cooling_amplitude_866)
    
        self.end = self.start + repump_dur_866
        