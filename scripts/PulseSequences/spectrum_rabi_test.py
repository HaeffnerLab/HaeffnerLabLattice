from labrad.units import WithUnit
from spectrum_rabi import spectrum_rabi

test_parameters = {
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
              'optical_pumping_frequency_729':WithUnit(0.0, 'MHz'),
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
              
              'rabi_excitation_frequency':WithUnit(0.0, 'MHz'),
              'rabi_excitation_amplitude':WithUnit(-3.0, 'dBm'),
              'rabi_excitation_duration':WithUnit(10.0, 'us'),
              
              'state_readout_frequency_397':WithUnit(110.0, 'MHz'),
              'state_readout_amplitude_397':WithUnit(-11.0, 'dBm'),
              'state_readout_frequency_866':WithUnit(80.0, 'MHz'),
              'state_readout_amplitude_866':WithUnit(-11.0, 'dBm'),
              'state_readout_duration':WithUnit(3.0,'ms'),
              
              'sideband_cooling_enable':False,
              'sideband_cooling_cycles': 4.0,
              'sideband_cooling_continuous':False,
              'sideband_cooling_pulsed':True,
              'sideband_cooling_duration_729_increment_per_cycle':WithUnit(0, 'us'),
              
              'sideband_cooling_continuous_duration':WithUnit(500, 'us'),
              'sideband_cooling_continuous_frequency_854':WithUnit(80.0, 'MHz'),
              'sideband_cooling_conitnuous_amplitude_854':WithUnit(-11.0, 'dBm'),
              'sideband_cooling_continuous_frequency_866':WithUnit(80.0, 'MHz'),
              'sideband_cooling_continuous_amplitude_866':WithUnit(-11.0, 'dBm'),
              'sideband_cooling_continuous_frequency_729':WithUnit(0.0, 'MHz'),
              'sideband_cooling_continuous_amplitude_729':WithUnit(-11.0, 'dBm'),
              'sideband_cooling_optical_pumping_duration':WithUnit(500, 'us'),
              
              'sideband_cooling_pulsed_duration_729':WithUnit(10, 'us'),
              'sideband_cooling_pulsed_cycles':10.0,
              
              'sideband_cooling_pulsed_duration_repumps':WithUnit(10, 'us'),
              'sideband_cooling_pulsed_duration_additional_866':WithUnit(10, 'us'),
              'sideband_cooling_pulsed_duration_between_pulses':WithUnit(5, 'us'),
              'sideband_cooling_pulsed_frequency_854':WithUnit(80.0, 'MHz'),
              'sideband_cooling_pulsed_amplitude_854':WithUnit(-3.0, 'dBm'),
              'sideband_cooling_pulsed_frequency_866':WithUnit(80.0, 'MHz'),
              'sideband_cooling_pulsed_amplitude_866':WithUnit(-3.0, 'dBm'),
              'sideband_cooling_pulsed_frequency_729':WithUnit(220.0, 'MHz'),
              'sideband_cooling_pulsed_amplitude_729':WithUnit(-13.0, 'dBm'),
              }



import labrad
import time
cxn = labrad.connect()
tinit = time.time()
cs = spectrum_rabi(**test_parameters)
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