from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.OpticalPumping import optical_pumping
from subsequences.RabiExcitation import rabi_excitation
from subsequences.Tomography import tomography_readout
from subsequences.SidebandCooling import sideband_cooling
from subsequences.TurnOffAll import turn_off_all
from subsequences.BlueHeating import blue_heating
from subsequences.SamplePID import sample_pid
from labrad.units import WithUnit

class blue_heat_rabi(pulse_sequence):
    
    required_parameters = [
                           ('OpticalPumping','optical_pumping_enable'), 
                           ('SidebandCooling','sideband_cooling_enable'),
                           ]
    
    required_subsequences = [turn_off_all,doppler_cooling_after_repump_d, optical_pumping,sideband_cooling,
                             blue_heating,rabi_excitation, tomography_readout, sample_pid
                             ]
    
    def sequence(self):
        p = self.parameters
        self.end = WithUnit(10, 'us')
        self.addSequence(turn_off_all)
        self.addSequence(sample_pid)
        
        self.addSequence(doppler_cooling_after_repump_d)
        if p.OpticalPumping.optical_pumping_enable:
            self.addSequence(optical_pumping)
        if p.SidebandCooling.sideband_cooling_enable:
            self.addSequence(sideband_cooling)
        self.addSequence(blue_heating)
        self.addSequence(rabi_excitation)
        self.addSequence(tomography_readout)