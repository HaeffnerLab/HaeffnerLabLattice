from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.OpticalPumping import optical_pumping
from subsequences.VAET import vaet
from subsequences.GlobalRotation import global_rotation
from subsequences.LocalRotation import local_rotation

from subsequences.Tomography import tomography_readout
from subsequences.TurnOffAll import turn_off_all
from subsequences.SidebandCooling import sideband_cooling
from subsequences.EmptySequence import empty_sequence
from labrad.units import WithUnit
from treedict import TreeDict
from subsequences.MolmerSorensen import molmer_sorensen

class MS_parity_flop(pulse_sequence):
    
    required_parameters = [ 
                           ('StatePreparation','optical_pumping_enable'), 
                           ('StatePreparation','sideband_cooling_enable'),
                           ('MolmerSorensen', 'SDDS_enable'),
                           ('MolmerSorensen', 'SDDS_rotate_out'),
                           ('MolmerSorensen', 'wait_time')
                           ]
    
    required_subsequences = [doppler_cooling_after_repump_d, optical_pumping, global_rotation, empty_sequence,
                             vaet, tomography_readout, turn_off_all, sideband_cooling, molmer_sorensen, local_rotation]

    replaced_parameters = {empty_sequence:[('EmptySequence','empty_sequence_duration'),]}
    
    def sequence(self):
        p = self.parameters
        wait_time=p.MolmerSorensen.wait_time
        self.end = WithUnit(10, 'us')
        self.addSequence(turn_off_all)
        
        self.addSequence(doppler_cooling_after_repump_d)
        if p.StatePreparation.optical_pumping_enable:
            self.addSequence(optical_pumping)
        if p.StatePreparation.sideband_cooling_enable:
            self.addSequence(sideband_cooling)
        #self.addSequence(global_rotation)
        #self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':WithUnit(2, 'ms')}))
        #self.addSequence(vaet)
        if p.MolmerSorensen.SDDS_enable:
            self.addSequence(local_rotation)
        self.addSequence(molmer_sorensen)
        if p.MolmerSorensen.SDDS_rotate_out:
            self.addSequence(local_rotation)
        # adding a controled waiting time
        self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':wait_time}))
        self.addSequence(global_rotation)
        self.addSequence(tomography_readout)
