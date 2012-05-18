from sequence import Sequence
import numpy as np
import math

class darkHeat(Sequence):
    #dictionary of variable: (type, min, max, default)
    requiredVars = {
                    'coolingTime':(float, 10e-9, 5.0, 10.0*10**-3),
                    'heatingTime':(float, 10e-9, 5.0, 10.0*10**-3),
                    'pulsedTime':(float, 10e-9, 5.0, 100.0*10**-6),
                    }
    
    def defineSequence(self):
        p = self.parameters
        pulser = self.pulser
        blue_cycle_time = 2 *  p.pulsedTime
        number_blue_cycles = int(math.floor(p.heatingTime / blue_cycle_time))
        recordTime = 2*(p.heatingTime + p.coolingTime)
        
        heatPulses866on = [('axial', 2*p.pulsedTime * i , p.pulsedTime) for i in range(number_blue_cycles) ]
        heatPulses866ff = [('axial', p.heatingTime + p.coolingTime + 2*p.pulsedTime * i , p.pulsedTime) for i in range(number_blue_cycles) ]
        
        pulser.add_ttl_pulse('TimeResolvedCount', 0.0, recordTime) #record the whole time
        pulser.add_ttl_pulse(('110DP',0.0, p.heatingTime))
        pulser.add_ttl_pulse(('110DP', p.heatingTime + p.coolingTime, p.heatingTime))
        pulser.add_ttl_pulse(('866DP', p.heatingTime + p.coolingTime, p.heatingTime))
        
        for pulses in [heatPulses866on, heatPulses866ff]:
            pulser.add_ttl_pulses(pulses)