from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.TurnOffAll import turn_off_all
from subsequences.DopplerCooling import doppler_cooling
from subsequences.EmptySequence import empty_sequence
from subsequences.BlueHeating import global_blue_heating, local_blue_heating
from subsequences.StateReadout import state_readout
from labrad.units import WithUnit

class melting_heat(pulse_sequence):
    
    required_parameters = [
                          'blue_heating_delay_before',
                          'blue_heating_delay_after', 
                          'use_local_blue_heating',
                          'crystallization_duration'
                          ]

    required_subsequences = [turn_off_all, doppler_cooling, empty_sequence, global_blue_heating, local_blue_heating, state_readout]

    def sequence(self):
        self.start_record_timetags = self.end
        self.end = WithUnit(10, 'us')
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)
        self.addSequence(empty_sequence, **{'empty_sequence_duration':self.blue_heating_delay_before})
        if self.use_local_blue_heating:
            self.addSequence(local_blue_heating)
        else:
            self.addSequence(global_blue_heating)
        self.addSequence(empty_sequence, **{'empty_sequence_duration':self.blue_heating_delay_after})
        self.begin_state_readout = self.end
        self.addSequence(state_readout)
        self.state_readout_duration = self.end - self.begin_state_readout
        self.addSequence(doppler_cooling, **{'doppler_cooling_duration':self.crystallization_duration})
        #record timetags the whole time
        self.timetag_record_duration = self.end - self.start_record_timetags
        self.addTTL('TimeResolvedCount', self.start_record_timetags, self.timetag_record_duration)


class sample_parameters(object):
    
    parameters = {              
              'doppler_cooling_frequency_397':WithUnit(110.0, 'MHz'),
              'doppler_cooling_amplitude_397':WithUnit(-11.0, 'dBm'),
              'doppler_cooling_frequency_866':WithUnit(80.0, 'MHz'),
              'doppler_cooling_amplitude_866':WithUnit(-11.0, 'dBm'),
              'doppler_cooling_repump_additional':WithUnit(100, 'us'),
              'doppler_cooling_duration':WithUnit(1.0,'ms'),
              
              'crystallization_duration':WithUnit(5.0,'ms'),
              
              'state_readout_frequency_397':WithUnit(110.0, 'MHz'),
              'state_readout_amplitude_397':WithUnit(-11.0, 'dBm'),
              'state_readout_frequency_866':WithUnit(80.0, 'MHz'),
              'state_readout_amplitude_866':WithUnit(-11.0, 'dBm'),
              'state_readout_duration':WithUnit(1.0,'ms'),
              
              'use_local_blue_heating': True,
              
              'blue_heating_delay_before':WithUnit(1.0,'ms'),
              'blue_heating_duration':WithUnit(1.0,'ms'),
              'blue_heating_repump_additional':WithUnit(3.0, 'us'),
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
    cs = melting_heat(**params)
    cs.programSequence(cxn.pulser)
    print 'to program', time.time() - tinit
    cxn.pulser.start_number(1)
    cxn.pulser.wait_sequence_done()
    cxn.pulser.stop_sequence()
    timetags = cxn.pulser.get_timetags().asarray
    print timetags
    readout = cxn.pulser.get_readout_counts().asarray
    print readout