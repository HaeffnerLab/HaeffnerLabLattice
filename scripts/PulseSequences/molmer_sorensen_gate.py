from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.OpticalPumping import optical_pumping
from subsequences.LocalRotation import local_rotation
from subsequences.MolmerSorensen import molmer_sorensen
from subsequences.Tomography import tomography_readout
from subsequences.TurnOffAll import turn_off_all
from subsequences.SidebandCooling import sideband_cooling
from labrad.units import WithUnit
from treedict import TreeDict

class ms_gate(pulse_sequence):
    
    required_parameters = [ 
                           ('OpticalPumping','optical_pumping_enable'), 
                           ('SidebandCooling','sideband_cooling_enable'),
                           ('MolmerSorensen', 'SDDS_enable'),
                           ]
    
    required_subsequences = [doppler_cooling_after_repump_d, optical_pumping, local_rotation,
                             molmer_sorensen, tomography_readout, turn_off_all, sideband_cooling]
    
    replaced_parameters = {
                           }

    def sequence(self):
        p = self.parameters
        self.end = WithUnit(10, 'us')
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling_after_repump_d)
        if p.OpticalPumping.optical_pumping_enable:
            self.addSequence(optical_pumping)
        if p.SidebandCooling.sideband_cooling_enable:
            self.addSequence(sideband_cooling)            
        if p.MolmerSorensen.SDDS_enable:
            self.addSequence(local_rotation)
        self.addSequence(molmer_sorensen)
        if p.MolmerSorensen.SDDS_enable:
            self.addSequence(local_rotation)
        self.addSequence(tomography_readout)