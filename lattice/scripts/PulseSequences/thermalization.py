from sequence import Sequence
import time

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
        
        #self.pulser.add_ttl_pulse('TimeResolvedCount', 0.0, recordTime) #record the whole time (for now)
        #self.pulser.add_ttl_pulse('110DP', 0.0, initial_cooling) #initial precooling with 110DP
        
        for pulse in range(probe_number):
            self.pulser.add_ttl_pulse('axial', initial_cooling + probe_off + pulse*probe_cycle, probe_on) #probe with the axial beam
            self.pulser.add_ttl_pulse('TimeResolvedCount', initial_cooling + probe_off + pulse*probe_cycle, probe_on) #record the whole time (for now)
            self.pulser.add_ttl_pulse('866DP', initial_cooling + probe_off + pulse*probe_cycle, probe_on)
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = thermalization(pulser)
    dv = cxn.data_vault
    dirappend = time.strftime("%Y%b%d_%H%M_%S",time.localtime())
    dv.cd(['','Experiments', 'thermalization', dirappend], True )
    dv.new('binnedFlourescence',[('Time', 'sec')], [('PMT counts','Arb','Arb')] )
    dv.add_parameter('plotLive',True)
    
    
    pulser.new_sequence()
    params = {
              'initial_cooling': 20e-3,
              'probe_number':1,
              'probe_off':10e-9,
              'probe_on':1e-3,
              }
    seq.setVariables(**params)
    seq.defineSequence()
    pulser.program_sequence()
    pulser.switch_auto('866DP', True) #high TTL means light ON
    for i in range(10000):
        print i
        pulser.reset_timetags()
        pulser.start_single()
        pulser.wait_sequence_done()
        pulser.stop_sequence()
        timetags = pulser.get_timetags().asarray
        print 'got {} timetags'.format(timetags.size)
        dv.add([i, timetags.size])
        time.sleep(10)
    print 'DONE'