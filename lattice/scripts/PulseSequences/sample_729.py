from sequence import Sequence

class sample_729(Sequence):
    
    requiredVars = {
                    'record':(float, 10e-9, 5.0, 100e-3),
                    }
    
    def defineSequence(self):   
        p = self.parameters
        pulser = self.pulser
        #caluclate time intervals
        self.recordTime =  p.record  
        pulser.add_ttl_pulse('TimeResolvedCount', 0.0 ,  2.0 )
        for i in range(20):
            pulser.add_dds_pulses('axial',[(40e-9 + i/20.0 , 190.0 + i , -13.0)])
            pulser.add_dds_pulses('729DP',[(40e-9  +i/20.0 , 250.0 - i , -33.0)])
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = sample_729(pulser)
    pulser.new_sequence()
    params = {
                'record':1000*10**-3,
              }
    seq.setVariables(**params)
    seq.defineSequence()
    pulser.program_sequence()
    pulser.reset_timetags()
    pulser.start_single()
    pulser.wait_sequence_done()
    pulser.stop_sequence()
    timetags = pulser.get_timetags().asarray
    print timetags.size