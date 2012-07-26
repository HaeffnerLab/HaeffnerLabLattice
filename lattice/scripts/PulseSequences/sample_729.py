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
        pulser.add_ttl_pulse('TimeResolvedCount', 0.0 ,  self.recordTime )
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    cxnlab = labrad.connect('192.168.169.49')
    pulser = cxn.pulser
    print cxnlab
    seq = sample_729(pulser)
    pulser.new_sequence()
    params = {
                'record':100*10**-3,
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