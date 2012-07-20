from sequence import Sequence

class PulsedScan(Sequence):
    #dictionary of variable: (type, min, max, default)
    requiredVars = {
                    'cooling_time':(float, 10e-9, 5.0,   1.0*10**-3),
                    'cooling_freq':(float, 90.0, 130.0,   110.0),
                    'cooling_ampl':(float, -63.0, -3.0,   -11.0),
                    'readout_time':(float, 10e-9, 5.0, 100.0*10**-6),
                    'readout_ampl_list':((list,float), -63.0, -3.0,   -11.0),
                    'readout_freq_list':((list,float), 90.0, 130.0, 110.0),
                    'switch_time':(float, 10e-9, 5.0,  100.0*10**-6),
                    }
    
    def defineSequence(self):
        p = self.parameters
        pulser = self.pulser
        offset = 40e-9
        
        freqs = p.readout_freq_list
        ampls = p.readout_ampl_list
        
        p.cycleTime = p.cooling_time + p.readout_time + 2*p.switch_time
        cT = p.cycleTime
        p.recordTime = p.cycleTime * len(freqs)
        p.startReadout =  p.cooling_time + p.switch_time
        p.stopReadout = p.startReadout + p.readout_time
        
        cooling = [ (offset + i  * cT, p.cooling_freq, p.cooling_ampl) for i,freq in enumerate(freqs) ]
        coolingOff = [ (offset + i  * cT + p.cooling_time, p.cooling_freq, -63.0) for i,freq in enumerate(freqs) ]
        readout = [ (offset + i  * cT + p.cooling_time + p.switch_time, freq, ampls[i]) for i,freq in enumerate(freqs) ]
        readoutOff = [ (offset + i  * cT + p.cooling_time + p.switch_time + p.readout_time, freq, -63.0) for i,freq in enumerate(freqs) ]
        
        #record timetags only during readouts
        for readoutStartTime in readout:
            pulser.add_ttl_pulse('TimeResolvedCount', readoutStartTime[0], p.readout_time)
        
        for pulses in [cooling, coolingOff, readout, readoutOff ]:
            pulser.add_dds_pulses('110DP', pulses)
        
if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    pulser = cxn.pulser
    seq = PulsedScan(pulser)
    pulser.new_sequence()
    params = {
            'cooling_time':1.0*10**-3,
            'cooling_freq':110.0,
            'cooling_ampl':-11.0,
            'readout_time':100.0*10**-6,
            'switch_time':100.0*10**-6,
            'readout_ampl_list':[-11.0, -12.0],
            'readout_freq_list':[110.0, 115.0],
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