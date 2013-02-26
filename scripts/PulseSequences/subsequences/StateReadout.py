from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from lattice.scripts.PulseSequences.subsequences.DopplerCooling import doppler_cooling
from treedict import TreeDict

class state_readout(pulse_sequence):
    
    
    required_parameters = [
                ('StateReadout','state_readout_frequency_397'), 
                ('StateReadout','state_readout_amplitude_397'), 
                ('StateReadout','state_readout_frequency_866'), 
                ('StateReadout','state_readout_amplitude_866'), 
                ('StateReadout','state_readout_duration'),
                ]

    required_subsequences = [doppler_cooling]
    
    def sequence(self):
        st = self.parameters.StateReadout
        replace = {
                   'DopplerCooling.doppler_cooling_frequency_397':st.state_readout_frequency_397,
                   'DopplerCooling.doppler_cooling_amplitude_397':st.state_readout_amplitude_397,
                   'DopplerCooling.doppler_cooling_frequency_866':st.state_readout_frequency_866,
                   'DopplerCooling.doppler_cooling_amplitude_866':st.state_readout_amplitude_866,
                   'DopplerCooling.doppler_cooling_duration':st.state_readout_duration,
                   }
        self.addSequence(doppler_cooling, TreeDict.fromdict(replace))
        self.addTTL('ReadoutCount', self.start, st.state_readout_duration)