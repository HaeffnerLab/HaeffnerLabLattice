from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence

class record_timetags(pulse_sequence):
    
    required_parameters = ['record_timetags_duration']
    
    def sequence(self):
        self.end = self.start + self.record_timetags_duration
        self.ttl_pulses.append(('TimeResolvedCount', self.start, self.record_timetags_duration))