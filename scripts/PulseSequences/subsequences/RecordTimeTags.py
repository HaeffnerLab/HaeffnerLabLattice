from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence

class record_timetags(pulse_sequence):
    
    required_parameters = [('RecordTimetags','record_timetags_duration')]
    
    def sequence(self):
        self.end = self.start + self.parameters.RecordTimetags.record_timetags_duration
        self.addTTL('TimeResolvedCount', self.start, self.parameters.RecordTimetags.record_timetags_duration)