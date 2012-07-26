from sequence import Sequence

class sample_729(Sequence):
    
    requiredVars = {
                    'record':(float, 10e-9, 5.0, 100e-3),
                    }
    
    def defineSequence(self):   
        p = self.parameters
        pulser = self.pulser
        pulser729 = self.pulser729
        #caluclate time intervals
        self.recordTime =  p.record  
        pulser.add_ttl_pulse('TimeResolvedCount', 0.0 ,  self.recordTime )
        pulser729.add_dds_pulses('729DP',[(0.1 , 220.0 , -33.0, 0.0)])
        pulser729.add_dds_pulses('729DP',[(0.5 , 220.0 , -33.0, 180.0)])
        pulser.add_dds_pulses('110DP',[(0.1 , 110.0 , -63.0)])
        pulser.add_dds_pulses('110DP',[(0.5 , 110.0 , -63.0)])
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    cxnlab = labrad.connect('192.168.169.49')
    pulser = cxn.pulser
    pulser729 = cxnlab.pulser_729
    seq = sample_729([pulser, pulser729])
    pulser.new_sequence()
    pulser729.new_sequence()
    params = {
                'record':1000*10**-3,
              }
    seq.setVariables(**params)
    seq.defineSequence()
    pulser.program_sequence()
    pulser729.program_sequence()
    pulser.reset_timetags()
    pulser.start_single()
    pulser.wait_sequence_done()
    pulser.stop_sequence()
    pulser729.stop_sequence()
    timetags = pulser.get_timetags().asarray
    print timetags.size