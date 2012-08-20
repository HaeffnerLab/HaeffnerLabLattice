from PulseSequence import PulseSequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.EmptySequence import empty_sequence
from subsequences.OpticalPumpingContinuous import optical_pumping_continuous
from subsequences.RabiExcitation import rabi_excitation
from subsequences.StateReadout import state_readout

class spectrum_rabi(PulseSequence):
    
    @staticmethod
    def configuration():
        config = [
                  'heating_time'
                  ]
        return config
    
    @staticmethod
    def needs_subsequences():
        seqs = [
                doppler_cooling_after_repump_d,
                optical_pumping_continuous,
                empty_sequence,
                rabi_excitation,
                state_readout,
                ]
        return seqs
    
    def sequence(self):
        self.addSequence(doppler_cooling_after_repump_d)
        self.addSequence(optical_pumping_continuous)
        self.addSequence(empty_sequence, **{'empty_sequence_duration':self.p.heating_time})
        self.addSequence(rabi_excitation)
        self.addSequence(state_readout)
        print self.dds_pulses

if __name__ == '__main__':
    from labrad import types as T
    required = spectrum_rabi.requiredParameters(returnDict = True)
    print 'required', required
    values = {
              'repump_d_duration':T.Value(500, 'us'),
              'repump_d_frequency_854':T.Value(80.0, 'MHz'),
              'repump_d_amplitude_854':T.Value(-11.0, 'dBm'),
              
              'doppler_cooling_frequency_397':T.Value(110.0, 'MHz'),
              'doppler_cooling_amplitude_397':T.Value(-11.0, 'dBm'),
              'doppler_cooling_frequency_866':T.Value(80.0, 'MHz'),
              'doppler_cooling_amplitude_866':T.Value(-11.0, 'dBm'),
              'doppler_cooling_duration':T.Value(1.0,'ms'),
              
              'optical_pumping_continuous_duration':T.Value(1, 'ms'),
              'optical_pumping_continuous_repump_additional':T.Value(500, 'us'),
              'optical_pumping_continuous_frequency_854':T.Value(80.0, 'MHz'),
              'optical_pumping_continuous_amplitude_854':T.Value(-11.0, 'dBm'),
              'optical_pumping_continuous_frequency_729':T.Value(220.0, 'MHz'),
              'optical_pumping_continuous_amplitude_729':T.Value(-11.0, 'dBm'),
              
              'heating_time':T.Value(0.0, 'ms'),
              
              'rabi_excitation_frequency':T.Value(220.0, 'MHz'),
              'rabi_excitation_amplitude':T.Value(-11.0, 'dBm'),
              'rabi_excitation_duration':T.Value(20.0, 'us'),
              
              'state_readout_frequency_397':T.Value(110.0, 'MHz'),
              'state_readout_amplitude_397':T.Value(-11.0, 'dBm'),
              'state_readout_frequency_866':T.Value(80.0, 'MHz'),
              'state_readout_amplitude_866':T.Value(-11.0, 'dBm'),
              'state_readout_duration':T.Value(1.0,'ms'),
              }
    
    cs = spectrum_rabi(**values)
    
    