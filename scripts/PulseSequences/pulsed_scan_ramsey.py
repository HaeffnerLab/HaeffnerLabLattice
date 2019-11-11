from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.OpticalPumping import optical_pumping
from subsequences.RabiExcitation import rabi_excitation
from subsequences.Tomography import tomography_readout
from subsequences.SidebandCooling import sideband_cooling
from subsequences.TurnOffAll import turn_off_all
from subsequences.BlueHeating import local_blue_heating
from subsequences.EmptySequence import empty_sequence
from subsequences.SamplePID import sample_pid
from treedict import TreeDict
from labrad.units import WithUnit

class pulsed_scan_ramsey(pulse_sequence):
    
    required_parameters = [
                           ('StatePreparation','optical_pumping_enable'), 
                           ('StatePreparation','sideband_cooling_enable'),
                           ('PulsedScanRamsey', 'pulse_duration'),
                           ('PulsedScanRamsey', 'ramsey_time'),
                           ]
    
    required_subsequences = [turn_off_all,doppler_cooling_after_repump_d, optical_pumping,sideband_cooling,
                             local_blue_heating,rabi_excitation, tomography_readout,empty_sequence, sample_pid
                             ]
    
    replaced_parameters = {local_blue_heating:[('Heating','blue_heating_duration')],
                           empty_sequence:[('EmptySequence','empty_sequence_duration')]
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
        self.addSequence(local_blue_heating, TreeDict.fromdict({'Heating.blue_heating_duration':p.PulsedScanRamsey.pulse_duration}))
        start_psk_ttl = self.end
        self.addSequence(empty_sequence, TreeDict.fromdict({'EmptySequence.empty_sequence_duration':p.PulsedScanRamsey.ramsey_time}))
        self.addSequence(local_blue_heating, TreeDict.fromdict({'Heating.blue_heating_duration':p.PulsedScanRamsey.pulse_duration}))
        duration_psk_ttl = self.end - start_psk_ttl
        self.addTTL('Phase_shift', start_psk_ttl, duration_psk_ttl)
        self.addSequence(rabi_excitation)
        self.addSequence(tomography_readout)
