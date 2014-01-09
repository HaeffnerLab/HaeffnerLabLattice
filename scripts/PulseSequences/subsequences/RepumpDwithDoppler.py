from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from RepumpD import repump_d
from DopplerCooling import doppler_cooling
from treedict import TreeDict

class doppler_cooling_after_repump_d(pulse_sequence):
    
    required_parameters = [('DopplerCooling','doppler_cooling_duration')]
    required_subsequences = [repump_d, doppler_cooling]
    replaced_parameters = {doppler_cooling:[('DopplerCooling','doppler_cooling_duration')]
                           }
    
    def sequence(self):
        dc_duration = self.parameters.DopplerCooling.doppler_cooling_duration
        #add the sequence
        self.addSequence(repump_d)
        stop_repump_d = self.end
        replacement = TreeDict.fromdict({'DopplerCooling.doppler_cooling_duration':stop_repump_d + dc_duration})
        self.addSequence(doppler_cooling, replacement, position = self.start)