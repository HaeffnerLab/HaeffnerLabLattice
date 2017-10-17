from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class Crystallization(pulse_sequence):
   
  
    def sequence(self):
        
        p = self.parameters.Crystallization 
        print "Turnning on the crystalization ttl"
        #print self.start
        print p.duration
        print  self.start
        #print p.repump_d_duration
        self.end = self.start + p.duration
        
        self.addTTL('crystallization', self.start, p.duration + WithUnit(0.2, 'us') )