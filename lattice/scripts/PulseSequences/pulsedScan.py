#        self.connectSignals(switchable)from sequence import Sequence

class PulsedScan(Sequence):
    #dictionary of variable: (type, min, max, default)
    requiredVars = {
                    'coolingTime':(float, 10e-9, 5.0, 10.0*10**-3),
                    'pulsedTime':(float, 10e-9, 5.0, 100.0*10**-6),
                    'switching':(float, 10e-9, 5.0, 2.0*10**-3),
                    'iterations':(int, 1, 1000, 1)
                    }
    
    def defineSequence(self):
        p = self.parameters
        pulser = self.pulser
        
        p.cycleTime = p.coolingTime + 2*p.pulsedTime + 2*p.switching
        recordTime = p.cycleTime * p.iterations
        startCooling =  [p.cycleTime * iter +  p.coolingTime for iter in range(p.iterations)] #sequence has TTL high then light OFF
        startPulses = [startCool + p.switching for startCool in startCooling]
        coolingPulses = [('110DP',start, 2*p.pulsedTime + 2*p.switching) for start in startCooling ]
        pulsedPulses = [('axial',start, 2*p.pulsedTime) for start in startPulses ]
        repumpOffPulses = [('866DP',start, p.pulsedTime) for start in startPulses ]
        
        pulser.add_ttl_pulse('TimeResolvedCount', 0.0, recordTime) #record the whole time
        for pulses in [coolingPulses, pulsedPulses,repumpOffPulses]:
            pulser.add_ttl_pulses(pulses)
        
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = PulsedScan(pulser)
    pulser.new_sequence()
    params = {
              'coolingTime':20.0*10**-3,
              'switching':1.0*10**-3,
              'pulsedTime':1*10**-3,
              'iterations':50,
            }
    seq.setVariables(**params)
    seq.defineSequence()
    pulser.program_sequence()
    pulser.reset_timetags()
    pulser.start_single()
    pulser.wait_sequence_done()
    pulser.stop_sequence()
    timetags = pulser.get_timetags().asarray
    print timetags