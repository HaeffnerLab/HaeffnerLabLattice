from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.OpticalPumping import optical_pumping
from subsequences.LocalRotation import local_rotation
from subsequences.MolmerSorensen import molmer_sorensen
from subsequences.GlobalRotation import global_rotation
from subsequences.Tomography import tomography_readout
from subsequences.TurnOffAll import turn_off_all
from subsequences.SidebandCooling import sideband_cooling
from labrad.units import WithUnit
from treedict import TreeDict

class ms_gate(pulse_sequence):
    
    required_parameters = [ 
                           ('StatePreparation','optical_pumping_enable'), 
                           ('StatePreparation','sideband_cooling_enable'),
                           ('MolmerSorensen', 'SDDS_enable'),
                           ('MolmerSorensen', 'SDDS_rotate_out'),
                           ('MolmerSorensen', 'analysis_pulse_enable'),
                           ]
    
    required_subsequences = [doppler_cooling_after_repump_d, optical_pumping, local_rotation,
                             molmer_sorensen, global_rotation, tomography_readout, turn_off_all, sideband_cooling]
    
    replaced_parameters = {
                           }

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
        if p.MolmerSorensen.SDDS_enable:
            self.addSequence(local_rotation)
        self.addSequence(molmer_sorensen)
        if p.MolmerSorensen.SDDS_rotate_out:
            self.addSequence(local_rotation)
            
        if p.MolmerSorensen.analysis_pulse_enable:
            self.addSequence(global_rotation)
        self.addSequence(tomography_readout)
