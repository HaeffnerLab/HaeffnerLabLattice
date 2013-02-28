from common.okfpgaservers.pulser.pulse_sequences.pulse_sequence import pulse_sequence
from subsequences.RepumpDwithDoppler import doppler_cooling_after_repump_d
from subsequences.EmptySequence import empty_sequence
from subsequences.OpticalPumping import optical_pumping
from subsequences.RabiExcitation import rabi_excitation, rabi_excitation_no_offset
from subsequences.StateReadout import state_readout
from subsequences.TurnOffAll import turn_off_all
from subsequences.BlueHeating import local_blue_heating
from labrad.units import WithUnit
           
class ramsey_dephase(pulse_sequence):
    
    required_parameters = [
                  'optical_pumping_enable','rabi_pi_time','pulse_gap',
                  'dephasing_enable', 'dephasing_frequency','dephasing_amplitude', 
                  'dephasing_duration','doppler_cooling_frequency_866','doppler_cooling_amplitude_866',
                  'second_pulse_duration',
                  ]

    required_subsequences = [doppler_cooling_after_repump_d, empty_sequence, optical_pumping, rabi_excitation, state_readout, turn_off_all, local_blue_heating, rabi_excitation_no_offset]
    
    def sequence(self):
        self.end = WithUnit(10, 'us')
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling_after_repump_d)
        if self.optical_pumping_enable:
            self.addSequence(optical_pumping)
        self.addSequence(rabi_excitation, **{'rabi_excitation_duration':self.rabi_pi_time / 2.0})
        if not self.dephasing_enable:
            self.addSequence(empty_sequence, **{'empty_sequence_duration':self.pulse_gap}) 
        else:
            spacing = (self.pulse_gap - self.dephasing_duration) / 2.0
            if spacing < WithUnit(5.0, 'us'): raise Exception("Ramsey Dephase, gap is too short to accomodate dephasing")
            self.addSequence(empty_sequence, **{'empty_sequence_duration':spacing}) 
            self.addSequence(local_blue_heating, **{
                                                'local_blue_heating_frequency_397': self.dephasing_frequency,
                                                'local_blue_heating_amplitude_397': self.dephasing_amplitude,
                                                'blue_heating_frequency_866': self.doppler_cooling_frequency_866,
                                                'blue_heating_amplitude_866': self.doppler_cooling_amplitude_866,
                                                'blue_heating_duration': self.dephasing_duration,
                                                'blue_heating_repump_additional': WithUnit(2, 'us')
                                                    }) 
            self.addSequence(empty_sequence, **{'empty_sequence_duration':spacing}) 
        self.addSequence(rabi_excitation_no_offset, **{'rabi_excitation_duration':self.second_pulse_duration})
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
              'optical_pumping_frequency_729':WithUnit(150.0, 'MHz'),
              'optical_pumping_frequency_854':WithUnit(80.0, 'MHz'),
              'optical_pumping_frequency_866':WithUnit(80.0, 'MHz'),
              'optical_pumping_amplitude_729':WithUnit(-11.0, 'dBm'),
              'optical_pumping_amplitude_854':WithUnit(-11.0, 'dBm'),
              'optical_pumping_amplitude_866':WithUnit(-11.0, 'dBm'),
              
              'optical_pumping_pulsed_cycles':5.0,
              'optical_pumping_pulsed_duration_729':WithUnit(20, 'us'),
              'optical_pumping_pulsed_duration_repumps':WithUnit(20, 'us'),
              'optical_pumping_pulsed_duration_additional_866':WithUnit(20, 'us'),
              'optical_pumping_pulsed_duration_between_pulses':WithUnit(5, 'us'),
              
              'optical_pumping_continuous':True,
              'optical_pumping_pulsed':False,
              
              'state_readout_frequency_397':WithUnit(110.0, 'MHz'),
              'state_readout_amplitude_397':WithUnit(-11.0, 'dBm'),
              'state_readout_frequency_866':WithUnit(80.0, 'MHz'),
              'state_readout_amplitude_866':WithUnit(-11.0, 'dBm'),
              'state_readout_duration':WithUnit(3.0,'ms'),
              
              'pulse_gap':WithUnit(100.0, 'us'),

              'rabi_pi_time':WithUnit(20.0, 'us'),
              'second_pulse_duration':WithUnit(10.0, 'us'),
              
              'dephasing_enable' : True,
              'dephasing_frequency':WithUnit(220.0, 'MHz'),
              'dephasing_amplitude':WithUnit(-11.0, 'dBm'),
              'dephasing_duration':WithUnit(5.0, 'us'),
              
              'rabi_excitation_frequency':WithUnit(220.0, 'MHz'),
              'rabi_excitation_amplitude':WithUnit(-3.0, 'dBm'),
              
              }

if __name__ == '__main__':
    import labrad
    import time
    cxn = labrad.connect()
    params = sample_parameters.parameters
    tinit = time.time()
    cs = ramsey_dephase(**params)
    cs.programSequence(cxn.pulser)
#    print 'to program', time.time() - tinit
#    cxn.pulser.start_number(1000)
#    cxn.pulser.wait_sequence_done()
#    cxn.pulser.stop_sequence()
#    readout = cxn.pulser.get_readout_counts().asarray
#    print readout
    dds = cxn.pulser.human_readable_dds()
    ttl = cxn.pulser.human_readable_ttl()
    print dds
    print ttl
    