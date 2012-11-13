from PulseSequence import PulseSequence
from subsequences.DopplerCooling import doppler_cooling
from subsequences.TurnOffAll import turn_off_all
from subsequences.EmptySequence import empty_sequence
from labrad.units import WithUnit

class branching_ratio(PulseSequence):
    
    def configuration(self):
        config = [
                  'cycles_per_sequence','between_pulses','duration_397_pulse','duration_866_pulse','frequency_397_pulse', 'frequency_866_pulse','amplitude_397_pulse', 'amplitude_866_pulse'
                  ]
        return config
    
    def sequence(self):
        p = self.p
        dds = self.dds_pulses
        cycles = int(p.cycles_per_sequence) #number of cycles, where each cycle is a pulse of 397 followed by pulse of 866
        #turn off all the lights, then do doppler cooling
        self.end = WithUnit(10, 'us')
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)
        #record timetags while switching while cycling 'wait, pulse 397, wait, pulse 866'
        start_recording_timetags = self.end
        for cycle in range(cycles):
            self.addSequence(empty_sequence, **{'empty_sequence_duration':p.between_pulses})
            dds.append( ('110DP',self.end, p.duration_397_pulse, p.frequency_397_pulse, p.amplitude_397_pulse) )
            self.end += p.duration_397_pulse
            self.addSequence(empty_sequence, **{'empty_sequence_duration':p.between_pulses})
            dds.append( ('110DP',self.end, p.duration_397_pulse, p.frequency_397_pulse, p.amplitude_397_pulse) )
            self.end += p.duration_397_pulse
            self.addSequence(empty_sequence, **{'empty_sequence_duration':p.between_pulses})
            dds.append( ('866DP',self.end, p.duration_866_pulse, p.frequency_866_pulse, p.amplitude_866_pulse) )
            self.end += p.duration_866_pulse
        stop_recording_timetags = self.end
        timetag_record_duration = stop_recording_timetags - start_recording_timetags
        #record timetags while cycling takes place
        self.ttl_pulses.append(('TimeResolvedCount',start_recording_timetags, timetag_record_duration))
        self.start_recording_timetags = start_recording_timetags
        self.timetag_record_cycle = 3 * p.between_pulses + 2 * p.duration_397_pulse + p.duration_866_pulse

class sample_parameters(object):
    
    parameters = {
                  #doppler cooling
                  'doppler_cooling_frequency_397':WithUnit(110.0, 'MHz'),
                  'doppler_cooling_amplitude_397':WithUnit(-11.0, 'dBm'),
                  'doppler_cooling_frequency_866':WithUnit(80.0, 'MHz'),
                  'doppler_cooling_amplitude_866':WithUnit(-11.0, 'dBm'),
                  'doppler_cooling_repump_additional':WithUnit(100, 'us'),
                  'doppler_cooling_duration':WithUnit(1.0,'ms'),
                  #cycling
                  'cycles_per_sequence':84,
                  'between_pulses':WithUnit(20, 'us'),
                  'duration_397_pulse':WithUnit(20, 'us'),
                  'duration_866_pulse':WithUnit(20, 'us'),
                  'frequency_397_pulse':WithUnit(110.0, 'MHz'),
                  'frequency_866_pulse':WithUnit(80.0, 'MHz'),
                  'amplitude_397_pulse':WithUnit(-11.0, 'dBm'),
                  'amplitude_866_pulse':WithUnit(-11.0, 'dBm'),
              }

if __name__ == '__main__':
    import labrad
    cxn = labrad.connect()
    params = sample_parameters.parameters
    cs = branching_ratio(**params)
    cs.programSequence(cxn.pulser)
    cxn.pulser.start_number(100)
    cxn.pulser.wait_sequence_done()
    cxn.pulser.stop_sequence()
    readout = cxn.pulser.get_timetags().asarray
    print 'got ' + len(readout) + ' timetags'