from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.SamplePID import sample_pid
from subsequences.OpticalPumping import optical_pumping
from subsequences.SZX import szx
from subsequences.Tomography import tomography_readout
from subsequences.TurnOffAll import turn_off_all
from subsequences.SidebandCooling import sideband_cooling
from subsequences.LocalRotation import local_pi_over_2_no_splocal
from labrad.units import WithUnit
from treedict import TreeDict

class szx_1ion(pulse_sequence):

    required_parameters = [ 
                           ('Heating', 'background_heating_time'),
                           ('StatePreparation','optical_pumping_enable'), 
                           ('StatePreparation','sideband_cooling_enable'),
                           ('SZX', 'second_pulse_phase'),
                           ]
    
    required_subsequences = [doppler_cooling_after_repump_d, optical_pumping, local_pi_over_2_no_splocal,
                             szx, tomography_readout, turn_off_all, sideband_cooling]
    
    replaced_parameters = {local_pi_over_2_no_splocal:[('LocalRotation','phase'),]}
    def sequence(self):

        p = self.parameters
        self.end = WithUnit(10, 'us')

        self.addSequence(turn_off_all)
        
        self.addSequence(doppler_cooling_after_repump_d)
        if p.StatePreparation.optical_pumping_enable:
            self.addSequence(optical_pumping)
        if p.StatePreparation.sideband_cooling_enable:
            self.addSequence(sideband_cooling)
        self.addSequence(local_pi_over_2_no_splocal, TreeDict.fromdict({'LocalRotation.phase':WithUnit(0.0, 'deg')}))
        self.addSequence(szx)
        self.addSequence(local_pi_over_2_no_splocal, TreeDict.fromdict({'LocalRotation.phase':p.SZX.second_pulse_phase}))
        self.addSequence(tomography_readout)
