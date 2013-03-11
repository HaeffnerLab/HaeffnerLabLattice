from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.SidebandCooling import sideband_cooling
from subsequences.OpticalPumping import optical_pumping
from subsequences.Tomography import tomography_readout
from subsequences.TurnOffAll import turn_off_all
from subsequences.Ramsey import ramsey_excitation

from labrad.units import WithUnit
           
class ramsey(pulse_sequence):
    
    required_parameters =  [('OpticalPumping','optical_pumping_enable'), 
                            ('SidebandCooling','sideband_cooling_enable'),
                            ('RepumpD_5_2','repump_d_duration'),
                            ('RepumpD_5_2','repump_d_frequency_854'),
                            ('RepumpD_5_2','repump_d_amplitude_854'),
                            ('DopplerCooling', 'doppler_cooling_frequency_397'),
                            ('DopplerCooling', 'doppler_cooling_amplitude_397'),
                            ('DopplerCooling', 'doppler_cooling_frequency_866'),
                            ('DopplerCooling', 'doppler_cooling_amplitude_866'),
                            ('DopplerCooling', 'doppler_cooling_repump_additional'),
                            ('DopplerCooling', 'doppler_cooling_duration'),
                          
                            ('OpticalPumping','optical_pumping_frequency_729'),
                            ('OpticalPumping','optical_pumping_frequency_854'),
                            ('OpticalPumping','optical_pumping_frequency_866'),
                            ('OpticalPumping','optical_pumping_amplitude_729'),
                            ('OpticalPumping','optical_pumping_amplitude_854'),
                            ('OpticalPumping','optical_pumping_amplitude_866'),
                            ('OpticalPumping','optical_pumping_type'),
                          
                            ('OpticalPumpingContinuous','optical_pumping_continuous_duration'),
                            ('OpticalPumpingContinuous','optical_pumping_continuous_repump_additional'),
                          
                            ('OpticalPumpingPulsed','optical_pumping_pulsed_cycles'),
                            ('OpticalPumpingPulsed','optical_pumping_pulsed_duration_729'),
                            ('OpticalPumpingPulsed','optical_pumping_pulsed_duration_repumps'),
                            ('OpticalPumpingPulsed','optical_pumping_pulsed_duration_additional_866'),
                            ('OpticalPumpingPulsed','optical_pumping_pulsed_duration_between_pulses'),
            
                            ('SidebandCooling','sideband_cooling_cycles'),
                            ('SidebandCooling','sideband_cooling_type'),
                            ('SidebandCooling','sideband_cooling_duration_729_increment_per_cycle'),
                            ('SidebandCooling','sideband_cooling_frequency_854'),
                            ('SidebandCooling','sideband_cooling_amplitude_854'),
                            ('SidebandCooling','sideband_cooling_frequency_866'),
                            ('SidebandCooling','sideband_cooling_amplitude_866'),
                            ('SidebandCooling','sideband_cooling_frequency_729'),
                            ('SidebandCooling','sideband_cooling_amplitude_729'),
                            ('SidebandCooling','sideband_cooling_optical_pumping_duration'),
                          
                            ('SidebandCoolingContinuous','sideband_cooling_continuous_duration'),
                          
                            ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_729'),
                            ('SidebandCoolingPulsed','sideband_cooling_pulsed_cycles'),
                            ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_repumps'),
                            ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_additional_866'),
                            ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_between_pulses'),

                            ('Excitation_729','rabi_excitation_frequency'),
                            ('Excitation_729','rabi_excitation_amplitude'),

                            ('StateReadout','state_readout_frequency_397'),
                            ('StateReadout','state_readout_amplitude_397'),
                            ('StateReadout','state_readout_frequency_866'),
                            ('StateReadout','state_readout_amplitude_866'),
                            ('StateReadout','state_readout_duration'),
                            
                            ('Tomography', 'rabi_pi_time'),
                            ('Tomography', 'iteration'),
                            ('Tomography', 'tomography_excitation_frequency'),
                            ('Tomography', 'tomography_excitation_amplitude'),
                            
                            ('Ramsey','ramsey_time'),
                            ('Ramsey','rabi_pi_time'),
                            ('Ramsey','second_pulse_phase'),
                            ]

    required_subsequences = [doppler_cooling_after_repump_d, optical_pumping, 
                             tomography_readout, turn_off_all, sideband_cooling, ramsey_excitation]
                             
    def sequence(self):
        p = self.parameters
        self.end = WithUnit(10, 'us')
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling_after_repump_d)
        if p.OpticalPumping.optical_pumping_enable:
            self.addSequence(optical_pumping)
        if p.SidebandCooling.sideband_cooling_enable:
            self.addSequence(sideband_cooling)
        self.addSequence(ramsey_excitation)
        self.addSequence(tomography_readout)