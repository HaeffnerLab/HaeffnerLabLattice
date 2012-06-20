from sequence import Sequence

class scan729(Sequence):
    
    requiredVars = {
                    'backgroundMeasure':(float, 10e-9, 5.0, 100e-3),
                    'initial_cooling':(float, 10e-9, 5.0, 100e-3),
                    'optical_pumping':(float, 10e-9, 5.0, 100e-3),
                    'rabitime':(float, 10e-9, 5.0, 100e-3),
                    'readout_time':(float, 10e-9, 5.0, 100e-3),
                    'repump854':(float, 10e-9, 5.0, 100e-3),
                    'repumpPower':(float, -63.0, -3.0, -3.0),
                    'coolingFreq397':(float, 90.0, 130.0, 110.0),
                    'readoutFreq397':(float, 90.0, 130.0, 120.0),
                    'coolingPower397':(float, -63.0, -3.0, -11.0),
                    'readoutPower397':(float, -63.0, -3.0, -11.0),
                    }
    
    def defineSequence(self):   
        p = self.parameters
        pulser = self.pulser
        #caluclate time intervals
        self.recordTime =  p.backgroundMeasure  + p.initial_cooling + p.optical_pumping + p.rabitime + p.readout_time + p.repump854
        self.startRabi = p.backgroundMeasure +  p.initial_cooling + p.optical_pumping
        self.startReadout = self.startRabi + p.rabitime
        self.stopReadout =  self.startReadout + p.readout_time
        
        pulser.add_ttl_pulse('TimeResolvedCount', 0.0 ,  self.recordTime )
        #measure_background
        pulser.add_ttl_pulse('866DP', 0.0, p.backgroundMeasure) #switch off 866 for background measure
        #initialize dds
        pulser.add_dds_pulses('110DP',[(40e-9 , p.coolingFreq397 , p.coolingPower397)])
        pulser.add_dds_pulses('854DP', [(40e-9 , 80.0 , -63.0)])
        #set dds
        pulser.add_dds_pulses('854DP', [(p.backgroundMeasure , 80.0 , p.repumpPower)])
        pulser.add_dds_pulses('854DP', [(p.backgroundMeasure +  p.initial_cooling , 80.0 , -63.0)])
        #optical pumping after p.backgroundMeasure + p.initial_cooling
        #also switch off 110DP here
        #rabi flop
        pulser.add_ttl_pulse('729DP', self.startRabi, p.rabitime)
        #switch off cooling while 729 is on
        pulser.add_ttl_pulse('866DP', self.startRabi, p.rabitime)
        pulser.add_ttl_pulse('110DP', self.startRabi, p.rabitime)
        #increase 397 intensity during readout
        pulser.add_dds_pulses('110DP',[(self.startReadout , p.readoutFreq397 , p.readoutPower397)])
        #after readout, repump back
        pulser.add_dds_pulses('110DP',[(self.stopReadout , p.coolingFreq397 , p.coolingPower397)])
        
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