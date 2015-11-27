from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.SidebandCooling import sideband_cooling
from subsequences.OpticalPumping import optical_pumping
from subsequences.Tomography import tomography_readout
from subsequences.TurnOffAll import turn_off_all
from subsequences.Ramsey import ramsey_excitation
from subsequences.BlueHeating import blue_heating
from subsequences.SamplePID import sample_pid
from labrad.units import WithUnit
           
class blue_heat_ramsey(pulse_sequence):
    
    required_parameters = [
                           ('OpticalPumping','optical_pumping_enable'), 
                           ('SidebandCooling','sideband_cooling_enable'),
                           ]

    required_subsequences = [doppler_cooling_after_repump_d,blue_heating,optical_pumping, tomography_readout,
                            turn_off_all,sideband_cooling,ramsey_excitation, sample_pid]
                             
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
        self.addSequence(ramsey_excitation)
        self.addSequence(tomography_readout)