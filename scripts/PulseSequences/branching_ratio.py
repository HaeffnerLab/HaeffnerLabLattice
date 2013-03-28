from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.DopplerCooling import doppler_cooling
from subsequences.TurnOffAll import turn_off_all
from subsequences.EmptySequence import empty_sequence
from treedict import TreeDict
from labrad.units import WithUnit

class branching_ratio(pulse_sequence):

    required_parameters = [
                  #number of cycles, where each cycle is a complete transfer from S to P to D and then back to S
                  ('BranchingRatio','cycles_per_sequence'),
                  ('BranchingRatio','between_pulses'),
                  ('BranchingRatio','duration_397_pulse_1'),
                  ('BranchingRatio','duration_397_pulse_2'),
                  ('BranchingRatio','duration_866_pulse'),
                  ('BranchingRatio','amplitude_866_pulse'),
                  ('BranchingRatio','amplitude_397_pulse_1'),
                  ('BranchingRatio','amplitude_397_pulse_2'),
                  ('DopplerCooling', 'doppler_cooling_frequency_397'),
                  ('DopplerCooling', 'doppler_cooling_amplitude_397'),
                  ('DopplerCooling', 'doppler_cooling_frequency_866'),
                  ('DopplerCooling', 'doppler_cooling_amplitude_866'),
                  ('DopplerCooling', 'doppler_cooling_repump_additional'),
                  ('DopplerCooling', 'doppler_cooling_duration'),
                  ]
    
    required_subsequences = [doppler_cooling, turn_off_all, empty_sequence]
    
    def sequence(self):
        cycles = int(self.parameters.BranchingRatio.cycles_per_sequence)
        #turn off all the lights, then do doppler cooling
        self.end = WithUnit(10, 'us')
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)
        #cycling parameters
        freq397 = self.parameters.DopplerCooling.doppler_cooling_frequency_397
        freq866 = self.parameters.DopplerCooling.doppler_cooling_frequency_866
        dur397_1 = self.parameters.BranchingRatio.duration_397_pulse_1
        dur397_2 = self.parameters.BranchingRatio.duration_397_pulse_2
        dur866 = self.parameters.BranchingRatio.duration_866_pulse
        ampl397_1 = self.parameters.BranchingRatio.amplitude_397_pulse_1
        ampl397_2 = self.parameters.BranchingRatio.amplitude_397_pulse_2
        ampl866 = self.parameters.BranchingRatio.amplitude_866_pulse
        between = self.parameters.BranchingRatio.between_pulses
        #record timetags while switching while cycling 'wait, pulse 397, wait, pulse 866'
        start_recording_timetags = self.end
        for cycle in range(cycles):
            self.addTTL('866DP',self.end, 5*between+2*(dur397_1+dur397_2))
            #self.addTTL('110DP',self.end, between)
            self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':between}))
            self.addDDS('397',self.end, dur397_1, freq397, ampl397_1)
            self.end += dur397_1
            self.addTTL('110DP',self.end, between)
            self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':between}))
            self.addDDS('397',self.end, dur397_2, freq397, ampl397_2)
            self.end += dur397_2     
            self.addTTL('110DP',self.end, between)
            self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':between}))
            self.addDDS('397',self.end, dur397_1, freq397, ampl397_1)
            self.end += dur397_1
            self.addTTL('110DP',self.end, between)
            self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':between}))
            self.addDDS('397',self.end, dur397_2, freq397, ampl397_2)
            self.end += dur397_2
            self.addTTL('110DP',self.end, between+dur866)
            self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':between}))            
            self.addDDS('866',self.end, dur866, freq866, ampl866)  
            self.end += dur866
        stop_recording_timetags = self.end
        timetag_record_duration = stop_recording_timetags - start_recording_timetags
        #record timetags while cycling takes place
        self.addTTL('TimeResolvedCount',start_recording_timetags, timetag_record_duration)
        #self.addTTL('866DP',start_recording_timetags, timetag_record_duration)
        self.start_recording_timetags = start_recording_timetags
        self.timetag_record_cycle = 5 * between + 2 * dur397_1 + 2 * dur397_2 + dur866