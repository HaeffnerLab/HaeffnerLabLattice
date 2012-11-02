from PulseSequence import PulseSequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.EmptySequence import empty_sequence
from subsequences.OpticalPumping import optical_pumping
from subsequences.RabiExcitation import rabi_excitation
from subsequences.StateReadout import state_readout
from subsequences.TurnOffAll import turn_off_all
from subsequences.GlobalBlueHeating import global_blue_heating
from labrad import types as T

class blue_heat_rabi(PulseSequence):
    
    def configuration(self):
        config = [
                  'background_heating_time','optical_pumping_enable','global_blue_heating_delay_before','global_blue_heating_delay_after'
                  ]
        return config
    
    def sequence(self):
        self.end = T.Value(10, 'us')
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling_after_repump_d)
        if self.p.optical_pumping_enable:
            self.addSequence(optical_pumping)
        self.addSequence(empty_sequence, **{'empty_sequence_duration':self.p.global_blue_heating_delay_before})
        self.addSequence(global_blue_heating)
        self.addSequence(empty_sequence, **{'empty_sequence_duration':self.p.global_blue_heating_delay_after})
        self.addSequence(rabi_excitation)
        self.addSequence(state_readout)

class sample_parameters(object):
    
    parameters = {
              'repump_d_duration':T.Value(500, 'us'),
              'repump_d_frequency_854':T.Value(80.0, 'MHz'),
              'repump_d_amplitude_854':T.Value(-11.0, 'dBm'),
              
              'doppler_cooling_frequency_397':T.Value(110.0, 'MHz'),
              'doppler_cooling_amplitude_397':T.Value(-11.0, 'dBm'),
              'doppler_cooling_frequency_866':T.Value(80.0, 'MHz'),
              'doppler_cooling_amplitude_866':T.Value(-11.0, 'dBm'),
              'doppler_cooling_repump_additional':T.Value(100, 'us'),
              'doppler_cooling_duration':T.Value(1.0,'ms'),
              
              
              'optical_pumping_enable':True,
              
              'optical_pumping_continuous_duration':T.Value(1, 'ms'),
              'optical_pumping_continuous_repump_additional':T.Value(500, 'us'),
              'optical_pumping_frequency_729':T.Value(220.0, 'MHz'),
              'optical_pumping_frequency_854':T.Value(80.0, 'MHz'),
              'optical_pumping_frequency_866':T.Value(80.0, 'MHz'),
              'optical_pumping_amplitude_729':T.Value(-11.0, 'dBm'),
              'optical_pumping_amplitude_854':T.Value(-11.0, 'dBm'),
              'optical_pumping_amplitude_866':T.Value(-11.0, 'dBm'),
              
              'optical_pumping_pulsed_cycles':10.0,
              'optical_pumping_pulsed_duration_729':T.Value(20, 'us'),
              'optical_pumping_pulsed_duration_repumps':T.Value(20, 'us'),
              'optical_pumping_pulsed_duration_additional_866':T.Value(20, 'us'),
              'optical_pumping_pulsed_duration_between_pulses':T.Value(5, 'us'),
              
              'optical_pumping_continuous':False,
              'optical_pumping_pulsed':True,
              
              'background_heating_time':T.Value(0.0, 'ms'),
              
              'rabi_excitation_frequency':T.Value(220.0, 'MHz'),
              'rabi_excitation_amplitude':T.Value(-11.0, 'dBm'),
              'rabi_excitation_duration':T.Value(20.0, 'us'),
              
              'state_readout_frequency_397':T.Value(110.0, 'MHz'),
              'state_readout_amplitude_397':T.Value(-11.0, 'dBm'),
              'state_readout_frequency_866':T.Value(80.0, 'MHz'),
              'state_readout_amplitude_866':T.Value(-11.0, 'dBm'),
              'state_readout_duration':T.Value(1.0,'ms'),
              
              'global_blue_heating_delay_before':T.Value(1.0,'ms'),
              'global_blue_heating_frequency_397':T.Value(130.0, 'MHz'),
              'global_blue_heating_amplitude_397':T.Value(-11.0, 'dBm'),
              'global_blue_heating_frequency_866':T.Value(80.0, 'MHz'),
              'global_blue_heating_amplitude_866':T.Value(-11.0, 'dBm'),
              'global_blue_heating_duration':T.Value(1.0,'ms'),
              'global_blue_heating_delay_after':T.Value(1.0,'ms'),
              }

if __name__ == '__main__':
    import labrad
    import time
    cxn = labrad.connect()
    params = sample_parameters.parameters
    tinit = time.time()
    cs = blue_heat_rabi(**params)
    cs.programSequence(cxn.pulser)
    print 'to program', time.time() - tinit
    cxn.pulser.start_number(100)
    cxn.pulser.wait_sequence_done()
    cxn.pulser.stop_sequence()
    readout = cxn.pulser.get_readout_counts().asarray
    print readout