from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.DopplerCooling import doppler_cooling
from subsequences.TurnOffAll import turn_off_all
from subsequences.EmptySequence import empty_sequence
from treedict import TreeDict
from labrad.units import WithUnit

class bare_line_scan(pulse_sequence):

    required_parameters = [
                  #number of cycles, where each cycle is a complete transfer from S to P to D and then back to S
                  ('BareLineScan','cycles_per_sequence'),
                  ('BareLineScan','between_pulses'),
                  
                  ('BareLineScan','duration_397_pulse'),
                  ('BareLineScan','frequency_397_pulse'),
                  ('BareLineScan','amplitude_397_pulse'),
                  
                  ('BareLineScan','duration_866_pulse'),
                  ('BareLineScan','frequency_866_pulse'),
                  ('BareLineScan','amplitude_866_pulse'),
                 
                  ('DopplerCooling', 'doppler_cooling_frequency_397'),
                  ('DopplerCooling', 'doppler_cooling_amplitude_397'),
                  ('DopplerCooling', 'doppler_cooling_frequency_866'),
                  ('DopplerCooling', 'doppler_cooling_amplitude_866'),
                  ('DopplerCooling', 'doppler_cooling_repump_additional'),
                  ('DopplerCooling', 'doppler_cooling_duration'),
                  ]
    required_subsequences = [doppler_cooling, turn_off_all, empty_sequence]
    
    def sequence(self):
        l = self.parameters.BareLineScan
        cycles = int(l.cycles_per_sequence)
        #turn off all the lights, then do doppler cooling
        self.end = WithUnit(10, 'us')
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)      
        #record timetags while switching while cycling 'wait, pulse 397, wait, pulse 866'
        start_recording_timetags = self.end
        for i in range(cycles):
            self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':l.between_pulses}))
            self.addDDS('397',self.end, l.duration_397_pulse, l.frequency_397_pulse, l.amplitude_397_pulse)
            self.end += l.duration_397_pulse
            self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':l.between_pulses}))
            self.addDDS('866',self.end, l.duration_866_pulse, l.frequency_866_pulse, l.amplitude_866_pulse) ###changed from radial to 866 :Hong
            self.end += l.duration_866_pulse
        stop_recording_timetags = self.end
        timetag_record_duration = stop_recording_timetags - start_recording_timetags
        #record timetags while cycling takes place
        self.addTTL('TimeResolvedCount',start_recording_timetags, timetag_record_duration)
        self.start_recording_timetags = start_recording_timetags
        self.timetag_record_cycle = l.between_pulses + l.duration_397_pulse + l.duration_866_pulse+l.between_pulses