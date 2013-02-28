from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.SidebandCooling import sideband_cooling
from subsequences.OpticalPumping import optical_pumping
from subsequences.StateReadout import state_readout
from subsequences.TurnOffAll import turn_off_all
from subsequences.RamseyDephase import ramsey_dephase_excitation

from labrad.units import WithUnit
           
class ramsey_dephase(pulse_sequence):
    
    required_parameters =  [
                  ('RepumpD_5_2','repump_d_duration'):WithUnit(200, 'us'),
                  ('RepumpD_5_2','repump_d_frequency_854'):WithUnit(80.0, 'MHz'),
                  ('RepumpD_5_2','repump_d_amplitude_854'):WithUnit(-11.0, 'dBm'),
              
                  ('DopplerCooling', 'doppler_cooling_frequency_397'):WithUnit(110.0, 'MHz'),
                  ('DopplerCooling', 'doppler_cooling_amplitude_397'):WithUnit(-11.0, 'dBm'),
                  ('DopplerCooling', 'doppler_cooling_frequency_866'):WithUnit(80.0, 'MHz'),
                  ('DopplerCooling', 'doppler_cooling_amplitude_866'):WithUnit(-11.0, 'dBm'),
                  ('DopplerCooling', 'doppler_cooling_repump_additional'):WithUnit(100, 'us'),
                  ('DopplerCooling', 'doppler_cooling_duration'):WithUnit(1.0,'ms'),
              
                  ('OpticalPumping','optical_pumping_enable'):True,
                  ('OpticalPumping','optical_pumping_frequency_729'):WithUnit(0.0, 'MHz'),
                  ('OpticalPumping','optical_pumping_frequency_854'):WithUnit(80.0, 'MHz'),
                  ('OpticalPumping','optical_pumping_frequency_866'):WithUnit(80.0, 'MHz'),
                  ('OpticalPumping','optical_pumping_amplitude_729'):WithUnit(-10.0, 'dBm'),
                  ('OpticalPumping','optical_pumping_amplitude_854'):WithUnit(-3.0, 'dBm'),
                  ('OpticalPumping','optical_pumping_amplitude_866'):WithUnit(-11.0, 'dBm'),
                  ('OpticalPumping','optical_pumping_type'):'continuous',
                  
                  ('OpticalPumpingContinuous','optical_pumping_continuous_duration'):WithUnit(1, 'ms'),
                  ('OpticalPumpingContinuous','optical_pumping_continuous_repump_additional'):WithUnit(200, 'us'),
                  
                  ('OpticalPumpingPulsed','optical_pumping_pulsed_cycles'):2.0,
                  ('OpticalPumpingPulsed','optical_pumping_pulsed_duration_729'):WithUnit(20, 'us'),
                  ('OpticalPumpingPulsed','optical_pumping_pulsed_duration_repumps'):WithUnit(20, 'us'),
                  ('OpticalPumpingPulsed','optical_pumping_pulsed_duration_additional_866'):WithUnit(20, 'us'),
                  ('OpticalPumpingPulsed','optical_pumping_pulsed_duration_between_pulses'):WithUnit(5, 'us'),
    
                  ('SidebandCooling','sideband_cooling_enable'):True,
                  ('SidebandCooling','sideband_cooling_cycles'): 4.0,
                  ('SidebandCooling','sideband_cooling_type'):'continuous',
                  ('SidebandCooling','sideband_cooling_duration_729_increment_per_cycle'):WithUnit(0, 'us'),
                  ('SidebandCooling','sideband_cooling_frequency_854'):WithUnit(80.0, 'MHz'),
                  ('SidebandCooling','sideband_cooling_amplitude_854'):WithUnit(-11.0, 'dBm'),
                  ('SidebandCooling','sideband_cooling_frequency_866'):WithUnit(80.0, 'MHz'),
                  ('SidebandCooling','sideband_cooling_amplitude_866'):WithUnit(-11.0, 'dBm'),
                  ('SidebandCooling','sideband_cooling_frequency_729'):WithUnit(-10.0, 'MHz'),
                  ('SidebandCooling','sideband_cooling_amplitude_729'):WithUnit(-11.0, 'dBm'),
                  ('SidebandCooling','sideband_cooling_optical_pumping_duration'):WithUnit(500, 'us'),
                  
                  ('SidebandCoolingContinuous','sideband_cooling_continuous_duration'):WithUnit(500, 'us'),
                  
                  ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_729'):WithUnit(10, 'us'),
                  ('SidebandCoolingPulsed','sideband_cooling_pulsed_cycles'):10.0,
                  ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_repumps'):WithUnit(10, 'us'),
                  ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_additional_866'):WithUnit(10, 'us'),
                  ('SidebandCoolingPulsed','sideband_cooling_pulsed_duration_between_pulses'):WithUnit(5, 'us'),
              
                  ('StateReadout','state_readout_frequency_397'):WithUnit(110.0, 'MHz'),
                  ('StateReadout','state_readout_amplitude_397'):WithUnit(-11.0, 'dBm'),
                  ('StateReadout','state_readout_frequency_866'):WithUnit(80.0, 'MHz'),
                  ('StateReadout','state_readout_amplitude_866'):WithUnit(-11.0, 'dBm'),
                  ('StateReadout','state_readout_duration'):WithUnit(3.0,'ms'),
              
                  ('Ramsey','rabi_pi_time'):WithUnit(100.0, 'us'),
                  
                  ('RamseyDephase','pulse_gap'):WithUnit(100.0, 'us'),
                  ('RamseyDephase','dephasing_frequency'):WithUnit(220.0, 'MHz'),
                  ('RamseyDephase','dephasing_amplitude'):WithUnit(-11.0, 'dBm'),
                  ('RamseyDephase','dephasing_duration'):WithUnit(20.0,'us'),
                  ('RamseyDephase','second_pulse_duration'):WithUnit(100.0, 'us'),
                  
                  ('Excitation_729','rabi_excitation_frequency'):WithUnit(10.0, 'MHz'),
                  ('Excitation_729','rabi_excitation_amplitude'):WithUnit(-3.0, 'dBm'),
                     ]

    required_subsequences = [doppler_cooling_after_repump_d, optical_pumping, 
                             state_readout, turn_off_all, sideband_cooling, ramsey_dephase_excitation]
                             
    def sequence(self):
        p = self.parameters
        self.end = WithUnit(10, 'us')
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling_after_repump_d)
        if p.OpticalPumping.optical_pumping_enable:
            self.addSequence(optical_pumping)
        if p.SidebandCooling.sideband_cooling_enable:
            self.addSequence(sideband_cooling)
        self.addSequence(ramsey_dephase_excitation)
        self.addSequence(state_readout)