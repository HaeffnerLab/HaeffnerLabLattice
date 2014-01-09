from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.DopplerCooling import doppler_cooling
from subsequences.TurnOffAll import turn_off_all
from subsequences.EmptySequence import empty_sequence
from treedict import TreeDict
from labrad.units import WithUnit

class lifetime_p(pulse_sequence):

    required_parameters = [
                           ('LifetimeP','cycles_per_sequence'),
                           ('LifetimeP','between_pulses'),
                           ('LifetimeP','duration_397_pulse'),
                           ('LifetimeP','frequency_397_pulse'),
                           ('LifetimeP','amplitude_397_pulse'),
                           ('LifetimeP','duration_866_pulse'),
                           ('LifetimeP','frequency_866_pulse'),
                           ('LifetimeP','amplitude_866_pulse'),
                           ]
    required_subsequences = [doppler_cooling, turn_off_all, empty_sequence]
    replaced_parameters = {empty_sequence:[('EmptySequence','empty_sequence_duration')]                       
                           }
    
    def sequence(self):
        l = self.parameters.LifetimeP
        cycles = int(l.cycles_per_sequence)
        #turn off all the lights, then do doppler cooling
        self.end = WithUnit(10, 'us')
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)
        ### add hack before the new parsing method ####
        frequency_advance_duration = WithUnit(6, 'us')
        ampl_off = WithUnit(-63.0, 'dBm')
        self.addDDS('radial',self.end, frequency_advance_duration, l.frequency_397_pulse, ampl_off)
        self.addDDS('866',self.end, frequency_advance_duration, l.frequency_866_pulse, ampl_off) ###changed from radial to 866 :Hong
        self.end += frequency_advance_duration
        ### hack done ###########
        
        #record timetags while switching while cycling 'wait, pulse 397, wait, pulse 866'
        start_recording_timetags = self.end
        for i in range(cycles):
            self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':l.between_pulses}))
            self.addDDS('radial',self.end, l.duration_397_pulse, l.frequency_397_pulse, l.amplitude_397_pulse)
            self.end += l.duration_397_pulse
            #self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':l.between_pulses}))
            #self.addDDS('radial',self.end, l.duration_397_pulse, l.frequency_397_pulse, l.amplitude_397_pulse)
            #self.end += l.duration_397_pulse
            self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':l.between_pulses}))
            self.addDDS('866',self.end, l.duration_866_pulse, l.frequency_866_pulse, l.amplitude_866_pulse) ###changed from radial to 866 :Hong
            self.end += l.duration_866_pulse
        stop_recording_timetags = self.end
        timetag_record_duration = stop_recording_timetags - start_recording_timetags
        #record timetags while cycling takes place
        self.addTTL('TimeResolvedCount',start_recording_timetags, timetag_record_duration)
        self.start_recording_timetags = start_recording_timetags
        #self.timetag_record_cycle = 1 * (l.between_pulses + l.duration_397_pulse) + l.duration_866_pulse+l.between_pulses
        self.timetag_record_cycle = (l.between_pulses + l.duration_397_pulse) + l.duration_866_pulse+l.between_pulses
