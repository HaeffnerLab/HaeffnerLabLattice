from sequence import Sequence

class LatentHeat(Sequence):
    #dictionary of variable: (type, min, max, default)
    requiredVars = {
                    'iterations':(int, 1, 1000, 1),
                    'initial_cooling':(float, 10e-9, 5.0, 1e-3),
                    'heat_delay':(float, 10e-9, 5.0, 100e-6),
                    'axial_heat':(float, 10e-9, 5.0, 1e-6),
                    'readout_delay':(float, 10e-9, 5.0, 10e-6),
                    'readout_time':(float, 10e-9, 5.0,  1e-6),
                    }
    
    def defineSequence(self):
        iterations = self.vars['iterations']
        initial_cooling = self.vars['initial_cooling']
        heat_delay = self.vars['heat_delay']
        axial_heat = self.vars['axial_heat']
        readout_delay = self.vars['readout_delay']
        readout_time = self.vars['readout_time']
        
        iterCycle = initial_cooling + heat_delay + axial_heat + readout_delay + readout_time
        recordTime = iterations * iterCycle
        self.pulser.add_ttl_pulse('TimeResolvedCount', 0.0, recordTime) #record the whole time
        
        for i in range(iterations):
        
            self.pulser.add_ttl_pulse('110DP', initial_cooling, globalofftime) #turn off blue light during heating
            self.pulser.add_ttl_pulse('110DPlist', initial_cooling, 10e-6) #advance frequency of RS
            self.pulser.add_ttl_pulse('axial', startHeat, axial_heat) #heat with the far blue axial beam
            #make sure there is no cooling by also switching off 866 when there is no 397 light.
            self.pulser.add_ttl_pulse('866DP', initial_cooling, heat_delay )
            self.pulser.add_ttl_pulse('866DP', endHeat, readout_delay )
            self.pulser.add_ttl_pulse('camera', startReadout, 10e-6)
            self.pulser.add_ttl_pulse('110DPlist', start_xtal, 10e-6) #advance frequency of RS at the end of the sequence

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = LatentHeat(pulser)
    pulser.new_sequence()
    params = {
              'initial_cooling': 1.,
              'heat_delay':1.,
              'axial_heat':1.,
              'readout_delay':1.,
              'readout_time':1.
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