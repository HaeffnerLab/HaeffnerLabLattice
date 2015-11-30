from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.EmptySequence import empty_sequence
from subsequences.OpticalPumping import optical_pumping
from subsequences.RabiExcitation import rabi_excitation_select_channel
from subsequences.Tomography import tomography_readout
from subsequences.TurnOffAll import turn_off_all
from subsequences.SidebandCooling import sideband_cooling
from subsequences.SZX import szx
from labrad.units import WithUnit
from treedict import TreeDict

'''
Does an szx interaction followed by an analysis rabi pulse. For probing
the dynamics of the sxz interaction on the motional state of the oscillator.
'''

class szx_rabi(pulse_sequence):
    
    required_parameters = [ 
                           ('Heating', 'background_heating_time'),
                           ('StatePreparation','optical_pumping_enable'), 
                           ('StatePreparation','sideband_cooling_enable'),
                           ]
    
    required_subsequences = [doppler_cooling_after_repump_d,optical_pumping,
                             rabi_excitation_select_channel, szx, tomography_readout, turn_off_all, sideband_cooling]
    def sequence(self):
        p = self.parameters
        self.end = WithUnit(10, 'us')
        self.addSequence(turn_off_all)
        #self.addSequence(sample_pid)
        
        self.addSequence(doppler_cooling_after_repump_d)
        if p.StatePreparation.optical_pumping_enable:
            self.addSequence(optical_pumping)
        if p.StatePreparation.sideband_cooling_enable:
            self.addSequence(sideband_cooling)
        self.addSequence(szx)
        self.addSequence(rabi_excitation_select_channel)
        self.addSequence(tomography_readout)
