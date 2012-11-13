from PulseSequence import PulseSequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.EmptySequence import empty_sequence
from subsequences.OpticalPumping import optical_pumping
from subsequences.RabiExcitation import rabi_excitation
from subsequences.StateReadout import state_readout
from subsequences.TurnOffAll import turn_off_all
from subsequences.BlueHeating import global_blue_heating, local_blue_heating
from labrad.units import WithUnit

class blue_heat_rabi(PulseSequence):
    
    def configuration(self):
        config = [
                  'optical_pumping_enable','blue_heating_delay_before','blue_heating_delay_after', 'use_local_blue_heating'
                  ]
        return config
    
    def sequence(self):
        self.end = WithUnit(10, 'us')
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling_after_repump_d)
        self.start_record_timetags = self.end
        self.addSequence(empty_sequence, **{'empty_sequence_duration':self.p.blue_heating_delay_before})
        if self.p.use_local_blue_heating:
            self.addSequence(local_blue_heating)
        else:
            self.addSequence(global_blue_heating)
        self.addSequence(empty_sequence, **{'empty_sequence_duration':self.p.blue_heating_delay_after})
        self.timetag_record_duration = self.end - self.start_record_timetags
        self.ttl_pulses.append( ('TimeResolvedCount', self.start_record_timetags, self.timetag_record_duration))
        if self.p.optical_pumping_enable:
            self.addSequence(optical_pumping)
        self.addSequence(rabi_excitation)
        self.addSequence(state_readout)

class sample_parameters(object):
    
    parameters = {
              'repump_d_duration':WithUnit(200, 'us'),
              'repump_d_frequency_854':WithUnit(80.0, 'MHz'),
              'repump_d_amplitude_854':WithUnit(-11.0, 'dBm'),
              
              'doppler_cooling_frequency_397':WithUnit(110.0, 'MHz'),
              'doppler_cooling_amplitude_397':WithUnit(-11.0, 'dBm'),
              'doppler_cooling_frequency_866':WithUnit(80.0, 'MHz'),
              'doppler_cooling_amplitude_866':WithUnit(-11.0, 'dBm'),
              'doppler_cooling_repump_additional':WithUnit(100, 'us'),
              'doppler_cooling_duration':WithUnit(1.0,'ms'),
              
              
              'optical_pumping_enable':True,
              
              'optical_pumping_continuous_duration':WithUnit(1, 'ms'),
              'optical_pumping_continuous_repump_additional':WithUnit(500, 'us'),
              'optical_pumping_frequency_729':WithUnit(220.0, 'MHz'),
              'optical_pumping_frequency_854':WithUnit(80.0, 'MHz'),
              'optical_pumping_frequency_866':WithUnit(80.0, 'MHz'),
              'optical_pumping_amplitude_729':WithUnit(-11.0, 'dBm'),
              'optical_pumping_amplitude_854':WithUnit(-11.0, 'dBm'),
              'optical_pumping_amplitude_866':WithUnit(-11.0, 'dBm'),
              
              'optical_pumping_pulsed_cycles':10.0,
              'optical_pumping_pulsed_duration_729':WithUnit(20, 'us'),
              'optical_pumping_pulsed_duration_repumps':WithUnit(20, 'us'),
              'optical_pumping_pulsed_duration_additional_866':WithUnit(20, 'us'),
              'optical_pumping_pulsed_duration_between_pulses':WithUnit(5, 'us'),
              
              'optical_pumping_continuous':True,
              'optical_pumping_pulsed':False,
              
              'rabi_excitation_frequency':WithUnit(220.0, 'MHz'),
              'rabi_excitation_amplitude':WithUnit(-11.0, 'dBm'),
              'rabi_excitation_duration':WithUnit(20.0, 'us'),
              
              'state_readout_frequency_397':WithUnit(110.0, 'MHz'),
              'state_readout_amplitude_397':WithUnit(-11.0, 'dBm'),
              'state_readout_frequency_866':WithUnit(80.0, 'MHz'),
              'state_readout_amplitude_866':WithUnit(-11.0, 'dBm'),
              'state_readout_duration':WithUnit(1.0,'ms'),
              
              'use_local_blue_heating': False,
              
              'blue_heating_delay_before':WithUnit(1.0,'ms'),
              'blue_heating_duration':WithUnit(1.0,'ms'),
              'blue_heating_delay_after':WithUnit(1.0,'ms'),
              
              'global_blue_heating_frequency_397':WithUnit(130.0, 'MHz'),
              'local_blue_heating_frequency_397':WithUnit(220.0, 'MHz'),
              'global_blue_heating_amplitude_397':WithUnit(-11.0, 'dBm'),
              'local_blue_heating_amplitude_397':WithUnit(-11.0, 'dBm'),
              'blue_heating_frequency_866':WithUnit(80.0, 'MHz'),
              'blue_heating_amplitude_866':WithUnit(-11.0, 'dBm'),

              
              'blue_heating_frequency_866':WithUnit(80.0, 'MHz'),
              'blue_heating_amplitude_866':WithUnit(-11.0, 'dBm'),
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