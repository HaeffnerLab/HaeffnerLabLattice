from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.EmptySequence import empty_sequence
from subsequences.OpticalPumping import optical_pumping
from subsequences.RabiExcitation import rabi_excitation_select_channel
from subsequences.Tomography import tomography_readout
from subsequences.TurnOffAll import turn_off_all
from subsequences.SidebandCooling import sideband_cooling
from subsequences.motion_analysis import motion_analysis
from labrad.units import WithUnit
from treedict import TreeDict

class spectrum_rabi(pulse_sequence):
    
    required_parameters = [ 
                           ('Heating', 'background_heating_time'),
                           ('StatePreparation','optical_pumping_enable'), 
                           ('StatePreparation','sideband_cooling_enable'),
                           ('Motion_Analysis','excitation_enable')
                           ]
    
    required_subsequences = [doppler_cooling_after_repump_d, empty_sequence, optical_pumping, 
                             rabi_excitation_select_channel, tomography_readout, turn_off_all, sideband_cooling,
                             motion_analysis]
    
    replaced_parameters = {empty_sequence:[('EmptySequence','empty_sequence_duration'),]}

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
                    
        self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':p.Heating.background_heating_time}))
        
        if p.Motion_Analysis.excitation_enable:
            self.addSequence(motion_analysis)
                
        self.addSequence(rabi_excitation_select_channel)
        self.addSequence(tomography_readout)
