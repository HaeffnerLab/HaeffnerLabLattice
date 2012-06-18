from sequence import Sequence

class scan729(Sequence):
    
    requiredVars = {
                    'backgroundMeasure':(float, 10e-9, 5.0, 100e-3),
                    'initial_cooling':(float, 10e-9, 5.0, 100e-3),
                    'optical_pumping':(float, 10e-9, 5.0, 100e-3),
                    'rabitime':(float, 10e-9, 5.0, 100e-3),
                    'readout_time':(float, 10e-9, 5.0, 100e-3),
                    'repump854':(float, 10e-9, 5.0, 100e-3),
                    'repumpPower':(float, -63.0, -3.0, -3.0)
                    }
    
    def defineSequence(self):   
        p = self.parameters
        pulser = self.pulser
        
        self.recordTime =  p.backgroundMeasure  + p.initial_cooling + p.optical_pumping + p.rabitime + p.readout_time + p.repump854
        self.startRabi = p.backgroundMeasure +  p.initial_cooling + p.optical_pumping
        self.startReadout = self.startRabi + p.rabitime
        self.stopReadout =  self.startReadout + p.readout_time
        
        pulser.add_ttl_pulse('TimeResolvedCount', 0.0 ,  self.recordTime )
        #measure_background
        pulser.add_ttl_pulse('866DP', 0.0, p.backgroundMeasure) #switch off 866 for background measure
        
        #optical pumping after p.backgroundMeasure + p.initial_cooling
        #also switch off 110DP here
        
        #rabi flop
        pulser.add_ttl_pulse('729DP', self.startRabi, p.rabitime)
        #switch off cooling while 729 is on
        pulser.add_ttl_pulse('866DP', self.startRabi, p.rabitime)
        pulser.add_ttl_pulse('110DP', self.startRabi, p.rabitime)
        #readout happens as both 866 and 397 are now on
        #after readout, repump back
        pulser.add_dds_pulses('854DP', [(40e-9 , 80.0 , -63.0)])
        pulser.add_dds_pulses('854DP', [(self.stopReadout , 80.0 , p.repumpPower)])
        pulser.add_dds_pulses('854DP', [(self.recordTime , 80.0 , -63.0)])
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = scan729(pulser)
    pulser.new_sequence()
    params = {
                'backgroundMeasure':1*10**-3,
                'initial_cooling':5*10**-3,
                'optical_pumping':1*10**-3,
                'rabitime':5*10**-3,
                'readout_time':10*10**-3,
                'repump854':5*10**-3,
                'repumpPower':-3.0
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