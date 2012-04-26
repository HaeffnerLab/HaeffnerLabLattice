from sequence import Sequence

class PulsedScan(Sequence):
    #dictionary of variable: (type, min, max, default)
    requiredVars = {
                    'coolingTime':(float, 10e-9, 5.0, 10.0*10**-3),
                    'pulsedTime':(float, 10e-9, 5.0, 100.0*10**-6),
                    'switching':(float, 10e-9, 5.0, 2.0*10**-3),
                    'pulsedSteps':(int, 1, 100, 1),
                    'iterationsCycle':(int, 1, 20, 1)
                    }
    
    def defineSequence(self):
        p = self.parameters
        pulser = self.pulser
        
        cycleTime = p.coolingTime + p.pulsedTime + 2*p.switching
        totalCycles = p.pulsedSteps * p.iterationsCycle
        recordTime = cycleTime * totalCycles
        startCooling =  [cycleTime * iter for iter in range(totalCycles)]
        startPulses = [startCool + p.coolingTime + p.switching for startCool in startCooling]
        startSwitching = [cycleTime * (iter+1) for iter in range(totalCycles) ]
        coolingPulses = [('110DP',start, p.coolingTime) for start in startCooling ]
        pulsedPulses = [('axial',start, p.pulsedTime) for start in startPulses ]
        switchingPulses = [('110DPlist', start, 10e-6) for start in startSwitching]
        
        pulser.add_ttl_pulse('TimeResolvedCount', 0.0, recordTime) #record the whole time
        for pulses in [coolingPulses, pulsedPulses, switchingPulses]:
            pulser.add_ttl_pulses(pulses)
        
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect('192.168.169.254',password = 'lab')
    pulser = cxn.pulser
    seq = PulsedScan(pulser)
    pulser.new_sequence()
    params = {
              'coolingTime':10.0*10**-3,
              'switching':5.0*10**-3,
              'pulsedSteps':20,
              'iterationsCycle':3,
              'pulsedTime':1.0*10**-3
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