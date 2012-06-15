from sequence import Sequence

class scan729(Sequence):
    
    requiredVars = {
                         'initial_cooling':(float, 10e-9, 5.0, 100e-3),
                         'pump':(float, 10e-9, 5.0, 100e-3),
                         'rabitime':(float, 10e-9, 5.0, 100e-3),
                         'backgroundMeasure':(float, 10e-9, 5.0, 100e-3),
                         'readout_time':(float, 10e-9, 5.0, 100e-3),
                    }
    
    def defineSequence(self):   
        p = self.parameters
        pulser = self.pulser
        
        #backgroundMeasure = p.backgroundMeasure 
        
        self.inital_cool = p.backgroundMeasure + p.initial_cooling
        self.readytime = p.backgroundMeasure + p.initial_cooling + p.pump
        self.rabitempus = p.backgroundMeasure + p.initial_cooling + p.pump + p.rabitime 
        self.readtime = self.rabitempus + p.readout_time
        
        
        pulser.add_ttl_pulse('TimeResolvedCount', 0.0 , self.readtime )
        #cooling + optical pumping
        pulser.add_dds_pulses('397DP', [(0.0 +100e-9 , 80.0 , -3.0)])
        pulser.add_dds_pulses('866DP', [(0.0 +100e-9 , 80.0 , -63.0)])
        pulser.add_dds_pulses('866DP', [(p.backgroundMeasure , 220.0 , -3.0)])
        pulser.add_dds_pulses('397DP', [(self.inital_cool , 220.0 , -63.0)])
        pulser.add_dds_pulses('397pump', [(self.inital_cool, 220.0 , -3.0)])
        pulser.add_dds_pulses('397pump', [(self.readytime , 220.0 , -63.0)])
        pulser.add_dds_pulses('866DP', [(self.readytime , 80.0 , -63.0)])
        
        #pulser.add_dds_pulse('729DP', [(readytime* t, 80 , -3.0)])
        pulser.add_dds_pulses('854DP', [(self.readytime , 80.0 , -3.0)])
        pulser.add_ttl_pulse('729DP', self.readytime, p.rabitime)  #running to the laser room
        #pulser.add_dds_pulse('729DP', [(rabitempus+ t, 80, -63.0)])
        pulser.add_dds_pulses('854DP', [(self.rabitempus , 80.0 , -63.0)])
        
        pulser.add_dds_pulses('866DP', [(self.rabitempus , 80.0 , -3.0)])
        pulser.add_dds_pulses('397DP', [(self.rabitempus , 220.0 , -3.0)])
        pulser.add_dds_pulses('866DP', [(self.readtime , 80.0 , -63.0)])
        pulser.add_dds_pulses('397DP', [(self.readtime , 220.0 , -63.0)])
           
        
    
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = freqscan(pulser)
    pulser.new_sequence()
    params = {
              
              'initial_cooling':0.01,
              'pump':0.01,
              'rabitime':0.01,
              'backgroundMeasure':0.01,
              'readout_time':0.01,
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
    print seq.readtime