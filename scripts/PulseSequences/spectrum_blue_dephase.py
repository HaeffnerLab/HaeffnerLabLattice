from PulseSequence import PulseSequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.EmptySequence import empty_sequence
from subsequences.OpticalPumping import optical_pumping
from subsequences.RabiExcitation import rabi_excitation
from subsequences.StateReadout import state_readout
from subsequences.TurnOffAll import turn_off_all
from labrad import types as T

class spectrum_blue_dephase(PulseSequence):
    
    def configuration(self):
        config = [
                  'optical_pumping_enable','pulse_gap', 'dephasing_frequency_729','dephasing_amplitude_729', 'dephasing_duration_729',  'preparation_pulse_duration_729', 'rabi_excitation_amplitude','rabi_excitation_frequency' ''
                  ]
        return config
    
    def sequence(self):
        self.end = T.Value(10, 'us')
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling_after_repump_d)
        if self.p.optical_pumping_enable:
            self.addSequence(optical_pumping)
        print self.p.toDict()
        self.dds_pulses.append(('729DP', self.end, self.p.preparation_pulse_duration_729, self.p.rabi_excitation_frequency, self.p.rabi_excitation_amplitude))
        self.end += self.p.preparation_pulse_duration_729
        pulses = self.dds_pulses
        dur = self.p.dephasing_duration_729
        print self.p.dephasing_amplitude_729
        print self.end
        pulses.append(('729DP', self.end + self.p.pulse_gap /2.0 - dur / 2.0, dur, self.p.dephasing_frequency_729, self.p.dephasing_amplitude_729))
        self.end += self.p.pulse_gap
        print self.end
        self.addSequence(rabi_excitation) 
        self.addSequence(state_readout)

class sample_parameters(object):
    
    parameters = {
              'repump_d_duration':T.Value(200, 'us'),
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
              'optical_pumping_continuous_repump_additional':T.Value(200, 'us'),
              'optical_pumping_frequency_729':T.Value(220.0, 'MHz'),
              'optical_pumping_frequency_854':T.Value(80.0, 'MHz'),
              'optical_pumping_frequency_866':T.Value(80.0, 'MHz'),
              'optical_pumping_amplitude_729':T.Value(-11.0, 'dBm'),
              'optical_pumping_amplitude_854':T.Value(-11.0, 'dBm'),
              'optical_pumping_amplitude_866':T.Value(-11.0, 'dBm'),
              
              'optical_pumping_pulsed_cycles':5.0,
              'optical_pumping_pulsed_duration_729':T.Value(20, 'us'),
              'optical_pumping_pulsed_duration_repumps':T.Value(20, 'us'),
              'optical_pumping_pulsed_duration_additional_866':T.Value(20, 'us'),
              'optical_pumping_pulsed_duration_between_pulses':T.Value(5, 'us'),
              
              'optical_pumping_continuous':True,
              'optical_pumping_pulsed':False,
              
              
              'rabi_excitation_frequency':T.Value(220.0, 'MHz'),
              'rabi_excitation_amplitude':T.Value(-11.0, 'dBm'),
              'rabi_excitation_duration':T.Value(5.0, 'us'),
              
              'state_readout_frequency_397':T.Value(110.0, 'MHz'),
              'state_readout_amplitude_397':T.Value(-11.0, 'dBm'),
              'state_readout_frequency_866':T.Value(80.0, 'MHz'),
              'state_readout_amplitude_866':T.Value(-11.0, 'dBm'),
              'state_readout_duration':T.Value(3.0,'ms'),
              
              'pulse_gap':T.Value(10.0, 'us'),
              'dephasing_frequency_729':T.Value(220.0, 'MHz'),
              'dephasing_amplitude_729':T.Value(-11.0, 'dBm'),
              'dephasing_duration_729':T.Value(5.0, 'us'),
              
              'preparation_pulse_duration_729':T.Value(2.0, 'us')
              
              }

if __name__ == '__main__':
    import labrad
    import time
    cxn = labrad.connect()
    params = sample_parameters.parameters
    tinit = time.time()
    cs = spectrum_blue_dephase(**params)
    cs.programSequence(cxn.pulser)
    print 'to program', time.time() - tinit
    cxn.pulser.start_number(100)
    cxn.pulser.wait_sequence_done()
    cxn.pulser.stop_sequence()
    readout = cxn.pulser.get_readout_counts().asarray
    print readout