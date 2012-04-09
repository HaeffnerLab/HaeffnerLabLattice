from sequence import Sequence

class thermalization(Sequence):
    #dictionary of variable: (type, min, max, default)
    requiredVars = {
                         'initial_cooling':(float, 10e-9, 5.0, 100e-3),
                         'probe_number':(int, 1, 300, 5),
                         'probe_off':(float, 10e-9, 5.0, 100e-3),
                         'probe_on':(float, 10e-9, 5.0, 100e-3),
                    }
    
    def defineSequence(self):
        initial_cooling = self.vars['initial_cooling']
        probe_number = self.vars['probe_number']
        probe_off = self.vars['probe_off']
        probe_on = self.vars['probe_on']
        probe_cycle = probe_off + probe_on
        
        recordTime = initial_cooling + probe_number * (probe_off + probe_on) 
        
        self.pulser.add_ttl_pulse('TimeResolvedCount', 0.0, recordTime) #record the whole time (for now)
        self.pulser.add_ttl_pulse('110DP', 0.0, initial_cooling) #initial precooling with 110DP
        
        for pulse in range(probe_number):
            self.pulser.add_ttl_pulse('axial', initial_cooling + probe_off + pulse*probe_cycle, probe_on) #probe with the axial beam

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = thermalization(pulser)
    pulser.new_sequence()
    params = {
              'initial_cooling': 20e-3,
              'probe_number':100,
              'probe_off':10e-3,
              'probe_on':1e-3,
              }
    seq.setVariables(**params)
    seq.defineSequence()
    pulser.program_sequence()
    pulser.reset_timetags()
    pulser.start_single()
    pulser.wait_sequence_done()
    pulser.stop_sequence()
    timetags = pulser.get_timetags().asarray
    print 'got {} timetags'.format(timetags.size)