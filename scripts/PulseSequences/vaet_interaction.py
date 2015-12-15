from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.OpticalPumping import optical_pumping
from subsequences.VAET import vaet
from subsequences.LocalRotation import local_rotation
from subsequences.motion_analysis import motion_analysis
from subsequences.Tomography import tomography_readout
from subsequences.TurnOffAll import turn_off_all
from subsequences.SidebandCooling import sideband_cooling
from labrad.units import WithUnit
from treedict import TreeDict

class vaet_interaction(pulse_sequence):
    
    required_parameters = [ 
                           ('StatePreparation','optical_pumping_enable'), 
                           ('StatePreparation','sideband_cooling_enable'),
                           ('MolmerSorensen', 'SDDS_rotate_out'),
                           ('Motion_Analysis','excitation_enable')
                           ]
    
    required_subsequences = [doppler_cooling_after_repump_d, optical_pumping, local_rotation, motion_analysis,
                             vaet, tomography_readout, turn_off_all, sideband_cooling]

    replaced_parameters = {}

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
        if p.Motion_Analysis.excitation_enable:
            self.addSequence(motion_analysis)
        self.addSequence(local_rotation)
        self.addSequence(vaet)
        if p.MolmerSorensen.SDDS_rotate_out:
            self.addSequence(local_rotation)
        self.addSequence(tomography_readout)
