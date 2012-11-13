from lattice.scripts.PulseSequences.PulseSequence import PulseSequence

class record_timetags(PulseSequence):

    def configuration(self):
        config = [
                  'record_timetags_duration',
                  ]
        return config
    
    def sequence(self):
        self.end = self.start + self.p.record_timetags_duration
        self.ttl_pulses.append(('TimeResolvedCount', self.start, self.p.record_timetags_duration))