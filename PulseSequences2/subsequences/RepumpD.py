from common.devel.bum.sequences.pulse_sequence import pulse_sequence

class RepumpD(pulse_sequence):
   
  
    def sequence(self):
        p = self.parameters.RepumpD_5_2
        st = self.parameters.StateReadout 
        print "START- repump D"
        #print self.start
        #print "p.repump_d_duration"
        #print p.repump_d_duration
        self.end = self.start + p.repump_d_duration
        self.addDDS('854DP', self.start, p.repump_d_duration, p.repump_d_frequency_854, p.repump_d_amplitude_854)
        #self.addDDS ('866',self.start, p.repump_d_duration, st.state_readout_frequency_866, st.state_readout_amplitude_866)
        # changing the 866 from a dds to a rf source enabled by a switch
        self.addTTL('866DP', self.start, p.repump_d_duration )