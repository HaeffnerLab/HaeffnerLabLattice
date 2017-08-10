from common.devel.bum.sequences.pulse_sequence import pulse_sequence

class RepumpD(pulse_sequence):
   
  
    def sequence(self):
        p = self.parameters.RepumpD_5_2
        print "START"
        print self.start
        print "p.repump_d_duration"
        print p.repump_d_duration
        self.end = self.start + p.repump_d_duration
        self.addDDS('854DP', self.start, p.repump_d_duration, p.repump_d_frequency_854, p.repump_d_amplitude_854)