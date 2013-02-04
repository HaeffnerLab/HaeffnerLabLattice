from PulseSequence import PulseSequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.EmptySequence import empty_sequence
from subsequences.OpticalPumping import optical_pumping
from subsequences.RabiExcitation import rabi_excitation
from subsequences.StateReadout import state_readout
from subsequences.TurnOffAll import turn_off_all
from labrad.units import WithUnit

class spectrum_rabi(PulseSequence):
    
    def configuration(self):
        config = [
                  'background_heating_time','optical_pumping_enable'
                  ]
        return config
    
    def sequence(self):
        self.end = WithUnit(10, 'us')
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling_after_repump_d)
        if self.p.optical_pumping_enable:
            self.addSequence(optical_pumping)
        self.addSequence(empty_sequence, **{'empty_sequence_duration':self.p.background_heating_time})
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
              
              
              'optical_pumping_enable':False,
              
              'optical_pumping_continuous_duration':WithUnit(1, 'ms'),
              'optical_pumping_continuous_repump_additional':WithUnit(200, 'us'),
              'optical_pumping_frequency_729':WithUnit(220.0, 'MHz'),
              'optical_pumping_frequency_854':WithUnit(80.0, 'MHz'),
              'optical_pumping_frequency_866':WithUnit(80.0, 'MHz'),
              'optical_pumping_amplitude_729':WithUnit(-10.0, 'dBm'),
              'optical_pumping_amplitude_854':WithUnit(-3.0, 'dBm'),
              'optical_pumping_amplitude_866':WithUnit(-11.0, 'dBm'),
              
              'optical_pumping_pulsed_cycles':2.0,
              'optical_pumping_pulsed_duration_729':WithUnit(20, 'us'),
              'optical_pumping_pulsed_duration_repumps':WithUnit(20, 'us'),
              'optical_pumping_pulsed_duration_additional_866':WithUnit(20, 'us'),
              'optical_pumping_pulsed_duration_between_pulses':WithUnit(5, 'us'),
              
              'optical_pumping_continuous':True,
              'optical_pumping_pulsed':False,
              
              'background_heating_time':WithUnit(0.0, 'ms'),
              
              'rabi_excitation_frequency':WithUnit(220.0, 'MHz'),
              'rabi_excitation_amplitude':WithUnit(-3.0, 'dBm'),
              'rabi_excitation_duration':WithUnit(10.0, 'us'),
              
              'state_readout_frequency_397':WithUnit(110.0, 'MHz'),
              'state_readout_amplitude_397':WithUnit(-11.0, 'dBm'),
              'state_readout_frequency_866':WithUnit(80.0, 'MHz'),
              'state_readout_amplitude_866':WithUnit(-11.0, 'dBm'),
              'state_readout_duration':WithUnit(3.0,'ms'),
              }

if __name__ == '__main__':
    import labrad
    import time
    cxn = labrad.connect()
    params = sample_parameters.parameters
    tinit = time.time()
    cs = spectrum_rabi(**params)
    cs.programSequence(cxn.pulser)
    print 'to program', time.time() - tinit
    cxn.pulser.start_number(1)
    cxn.pulser.wait_sequence_done()
    cxn.pulser.stop_sequence()
    dds = cxn.pulser.human_readable_dds()
    print dds == [('pump', 109.99923704890517, -33.0004577706569), ('pump', 109.99923704890517, -63.0), ('pump', 109.99923704890517, -63.0), ('pump', 109.99923704890517, -63.0), ('pump', 109.99923704890517, -63.0), ('pump', 109.99923704890517, -63.0), ('pump', 109.99923704890517, -63.0), ('pump', 109.99923704890517, -63.0), ('pump', 109.99923704890517, -63.0), ('pump', 109.99923704890517, -63.0), ('854DP', 79.99923704890517, -33.0004577706569), ('854DP', 79.99923704890517, -63.0), ('854DP', 79.99923704890517, -11.0), ('854DP', 79.99923704890517, -63.0), ('854DP', 79.99923704890517, -63.0), ('854DP', 79.99923704890517, -63.0), ('854DP', 79.99923704890517, -63.0), ('854DP', 79.99923704890517, -63.0), ('854DP', 79.99923704890517, -63.0), ('854DP', 79.99923704890517, -63.0), ('radial', 219.99923704890517, -33.0004577706569), ('radial', 219.99923704890517, -63.0), ('radial', 219.99923704890517, -63.0), ('radial', 219.99923704890517, -63.0), ('radial', 219.99923704890517, -63.0), ('radial', 219.99923704890517, -63.0), ('radial', 219.99923704890517, -63.0), ('radial', 219.99923704890517, -63.0), ('radial', 219.99923704890517, -63.0), ('radial', 219.99923704890517, -63.0), ('729DP', 219.99999997671694, -33.0004577706569), ('729DP', 0.0, -63.0), ('729DP', 0.0, -63.0), ('729DP', 0.0, -63.0), ('729DP', 0.0, -63.0), ('729DP', 219.99999997671694, -63.0), ('729DP', 219.99999997671694, -3.0), ('729DP', 219.99999997671694, -63.0), ('729DP', 219.99999997671694, -63.0), ('729DP', 219.99999997671694, -63.0), ('866DP', 79.99923704890517, -33.0004577706569), ('866DP', 79.99923704890517, -63.0), ('866DP', 79.99923704890517, -11.0), ('866DP', 79.99923704890517, -11.0), ('866DP', 79.99923704890517, -11.0), ('866DP', 79.99923704890517, -63.0), ('866DP', 79.99923704890517, -63.0), ('866DP', 79.99923704890517, -11.0), ('866DP', 79.99923704890517, -11.0), ('866DP', 79.99923704890517, -63.0), ('110DP', 109.99923704890517, -33.0004577706569), ('110DP', 109.99923704890517, -63.0), ('110DP', 109.99923704890517, -11.0), ('110DP', 109.99923704890517, -11.0), ('110DP', 109.99923704890517, -63.0), ('110DP', 109.99923704890517, -63.0), ('110DP', 109.99923704890517, -63.0), ('110DP', 109.99923704890517, -11.0), ('110DP', 109.99923704890517, -63.0), ('110DP', 109.99923704890517, -63.0)]
    ttl = cxn.pulser.human_readable_ttl()
    print ttl == [['0.0', '00000000000000000000000000000000'], ['1e-05', '00000000000000000010000000000000'], ['1.008e-05', '00000000000000000000000000000000'], ['6e-05', '00000000000000000010000000000000'], ['6.008e-05', '00000000000000000000000000000000'], ['0.00026', '00000000000000000010000000000000'], ['0.00026008', '00000000000000000000000000000000'], ['0.00132', '00000000000000000010000000000000'], ['0.00132008', '00000000000000000000000000000000'], ['0.00142', '00000000000000000010000000000000'], ['0.00142008', '00000000000000000000000000000000'], ['0.001426', '00000000000000000010000000000000'], ['0.00142608', '00000000000000000000000000000000'], ['0.001436', '00000000000000000010100000000000'], ['0.00143608', '00000000000000000000100000000000'], ['0.004436', '00000000000000000010000000000000'], ['0.00443608', '00000000000000000000000000000000'], ['0.004536', '00000000000000000010000000000000'], ['0.00453608', '00000000000000000001000000000000'], ['0.00453616', '00000000000000000000000000000000'], ['0.0', '00000000000000000000000000000000']]
    readout = cxn.pulser.get_readout_counts().asarray
    print readout