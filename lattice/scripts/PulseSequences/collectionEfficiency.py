from sequence import Sequence

class collectionEfficiency(Sequence):
    #dictionary of variable: (type, min, max, default)
    requiredVars = {
                    'dopplerCooling':(float,  100e-9, 1.0, 100e-3),
                    'iterations':(int, 1, 2000, 1),
                    'repumpD':(float, 100e-9, 5.0, 10e-6),
                    'repumpDelay':(float, 100e-9, 5.0, 100e-9),
                    'exciteP':(float, 100e-9, 5.0, 1e-6),
                    'finalDelay':(float, 100e-9, 5.0, 1e-6),
                    'iterDelay':(float, 100e-9, 1.0, 1e-6)
                    }
    
    def defineSequence(self):
        dopplerCooling = self.vars['dopplerCooling']
        iterations = self.vars['iterations']
        repumpD = self.vars['repumpD']
        repumpDelay = self.vars['repumpDelay']
        exciteP = self.vars['exciteP']
        finalDelay = self.vars['finalDelay']
        iterDelay = self.vars['iterDelay']
        
        iterCycle = repumpD + repumpDelay + exciteP + finalDelay
        recordTime = dopplerCooling + iterDelay + iterations * iterCycle
        
        self.pulser.add_ttl_pulse('TimeResolvedCount', 0.0, recordTime) #record the whole time
        
        self.pulser.add_ttl_pulse('110DP', 0.0, dopplerCooling) 
        self.pulser.add_ttl_pulse('866DP', 0.0, dopplerCooling) 
        
        for i in range(iterations):
            print 'programming', i
            startCycle = dopplerCooling + iterDelay + i * iterCycle
            startRepump = startCycle + exciteP + repumpDelay
            self.pulser.add_ttl_pulse('110DP', startCycle, exciteP) #excite the P-level
            self.pulser.add_ttl_pulse('866DP', startRepump, repumpD) #repump the D level

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = collectionEfficiency(pulser)
    pulser.new_sequence()
    params = {
              'dopplerCooling':100e-3,
              'iterDelay':1e-6,
              'iterations': 2000,
              'repumpD':5.0*10**-6,
              'decayPS':100.0*10**-9,
              'exciteP':1.0*10**-6,
              'finalDelay':5.0*10**-6,
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